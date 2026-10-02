#!/usr/bin/env python3
"""Procura versões novas das imagens Docker dos apps da loja.

Para cada `image: repo:tag@sha256:...` dos docker-compose.yml, lista as tags do
registro e procura a maior versão com o mesmo formato da atual (mesmo prefixo,
mesmo sufixo e mesma quantidade de números: `v0.147.0-noble-nvidia` só é
comparada com `vX.Y.Z-noble-nvidia`). Tags sem número de versão (`latest`,
`nightly`, `pg18`) são ignoradas.

Uso:
  check_updates.py plan            # JSON com as atualizações encontradas
  check_updates.py apply           # aplica nos arquivos e escreve o corpo do PR
"""

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Imagens compiladas por esta loja: as tags novas vêm da imagem oficial e a nossa
# precisa ser compilada (workflow opengym-coach-image.yml) antes de aplicar.
OWN_BUILDS = {
    "ghcr.io/edu-ricardo/opengym-api-coach": "ghcr.io/duartesantos8/opengym-api",
}

IMAGE_LINE = re.compile(r"^(\s*image:\s*)(\S+)\s*$", re.M)
VERSION_NUMBER = re.compile(r"\d+(?:\.\d+)+")
INDEX_TYPES = ", ".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
])


def split_image(ref):
    name, _, digest = ref.partition("@")
    repo, _, tag = name.rpartition(":")
    if not repo or "/" in tag:
        return None
    return repo, tag, digest


def registry_of(repo):
    first = repo.split("/")[0]
    if "." in first or ":" in first:
        return first, repo[len(first) + 1:]
    path = repo if "/" in repo else f"library/{repo}"
    return "registry-1.docker.io", path


def token_for(registry, path):
    if registry == "registry-1.docker.io":
        url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{path}:pull"
    else:
        url = f"https://{registry}/token?scope=repository:{path}:pull"
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.load(r)
    return data.get("token") or data.get("access_token")


def list_tags(repo):
    registry, path = registry_of(repo)
    token = token_for(registry, path)
    url = f"https://{registry}/v2/{path}/tags/list?n=1000"
    tags = []
    for _ in range(200):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            tags += json.load(r).get("tags") or []
            link = r.headers.get("Link")
        if not link:
            break
        url = urllib.parse.urljoin(f"https://{registry}", re.search(r"<([^>]+)>", link).group(1))
    return tags


def digest_of(repo, tag):
    registry, path = registry_of(repo)
    token = token_for(registry, path)
    req = urllib.request.Request(
        f"https://{registry}/v2/{path}/manifests/{tag}",
        method="HEAD",
        headers={"Authorization": f"Bearer {token}", "Accept": INDEX_TYPES},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.headers["Docker-Content-Digest"]


def tag_pattern(tag):
    m = VERSION_NUMBER.search(tag)
    if not m:
        return None
    parts = m.group(0).count(".") + 1
    number = r"(\d+" + r"(?:\.\d+)" * (parts - 1) + ")"
    return re.compile("^" + re.escape(tag[: m.start()]) + number + re.escape(tag[m.end():]) + "$"), m.group(0)


def as_tuple(version):
    return tuple(int(x) for x in version.split("."))


def newest_tag(repo, tag):
    pattern = tag_pattern(tag)
    if not pattern:
        return None
    regex, current = pattern
    best, best_version = None, as_tuple(current)
    for candidate in list_tags(OWN_BUILDS.get(repo, repo)):
        m = regex.match(candidate)
        if m and as_tuple(m.group(1)) > best_version:
            best, best_version = candidate, as_tuple(m.group(1))
    return best


def read_field(manifest_text, field):
    m = re.search(rf'^{field}:\s*"?([^"\n]*)"?\s*$', manifest_text, re.M)
    return m.group(1).strip() if m else ""


def plan():
    apps = []
    for compose in sorted(ROOT.glob("*/docker-compose.yml")):
        manifest = compose.with_name("umbrel-app.yml")
        if not manifest.exists():
            continue
        manifest_text = manifest.read_text(encoding="utf-8")
        app = {
            "dir": compose.parent.name,
            "name": read_field(manifest_text, "name"),
            "version": read_field(manifest_text, "version"),
            "repo": read_field(manifest_text, "repo"),
            "updates": [],
            "skipped": [],
        }
        for _, ref in IMAGE_LINE.findall(compose.read_text(encoding="utf-8")):
            parsed = split_image(ref)
            if not parsed:
                continue
            repo, tag, _ = parsed
            try:
                new = newest_tag(repo, tag)
            except (urllib.error.URLError, KeyError, ValueError) as e:
                app["skipped"].append(f"{repo}:{tag} (erro: {e})")
                continue
            if new is None and not tag_pattern(tag):
                app["skipped"].append(f"{repo}:{tag} (tag sem número de versão)")
            if new:
                app["updates"].append({
                    "repo": repo, "old_ref": ref, "old_tag": tag, "new_tag": new,
                    "own_build": repo in OWN_BUILDS,
                })
        if app["updates"] or app["skipped"]:
            apps.append(app)
    return apps


def new_app_version(app):
    """Troca o número da versão do app pelo da imagem principal (a que tem o mesmo número)."""
    version = app["version"]
    for u in app["updates"]:
        old_number = VERSION_NUMBER.search(u["old_tag"]).group(0)
        new_number = VERSION_NUMBER.search(u["new_tag"]).group(0)
        if old_number in version:
            # "-rN" marca correções da loja sobre a mesma versão; some com a versão nova
            return re.sub(r"-r\d+$", "", version.replace(old_number, new_number, 1))
    return None


def apply(apps, body_path):
    lines = ["Atualizações encontradas pela verificação automática da loja.", ""]
    changed = False
    for app in apps:
        if not app["updates"]:
            continue
        folder = ROOT / app["dir"]
        compose = folder / "docker-compose.yml"
        text = compose.read_text(encoding="utf-8")
        for u in app["updates"]:
            digest = digest_of(u["repo"], u["new_tag"])
            text = text.replace(u["old_ref"], f'{u["repo"]}:{u["new_tag"]}@{digest}')
        compose.write_text(text, encoding="utf-8", newline="\n")

        version = new_app_version(app)
        manifest = folder / "umbrel-app.yml"
        if version:
            m_text = manifest.read_text(encoding="utf-8")
            m_text = re.sub(r'^version:.*$', f'version: "{version}"', m_text, count=1, flags=re.M)
            manifest.write_text(m_text, encoding="utf-8", newline="\n")
        changed = True

        lines.append(f'### {app["name"]}  `{app["version"]}` → `{version or app["version"]}`')
        for u in app["updates"]:
            note = " (compilada por esta loja)" if u["own_build"] else ""
            lines.append(f'- `{u["repo"]}`: `{u["old_tag"]}` → `{u["new_tag"]}`{note}')
        if not version:
            lines.append("- ⚠️ Só imagens auxiliares mudaram: a versão do app não foi alterada, então o "
                         "Umbrel só entrega isso junto com a próxima atualização da imagem principal.")
        if app["repo"]:
            lines.append(f'- Notas de versão: {app["repo"].rstrip("/")}/releases')
        lines.append("")

    skipped = [(a["name"], s) for a in apps for s in a["skipped"]]
    if skipped:
        lines += ["<details><summary>Imagens não verificadas</summary>", ""]
        lines += [f"- {name}: `{s}`" for name, s in skipped]
        lines += ["", "</details>", ""]
    lines += ["Revise as notas de versão antes do merge: o Umbrel oferece a atualização assim que "
              "isto entrar na `main`."]
    Path(body_path).write_text("\n".join(lines), encoding="utf-8")
    return changed


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "plan"
    found = plan()
    if command == "plan":
        print(json.dumps(found, indent=2, ensure_ascii=False))
    elif command == "apply":
        print("changed" if apply(found, sys.argv[2] if len(sys.argv) > 2 else "pr-body.md") else "unchanged")
    else:
        sys.exit(f"comando desconhecido: {command}")

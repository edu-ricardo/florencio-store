# Florencio Store

Loja de comunidade (Community App Store) para o umbrelOS.

## Como instalar no seu Umbrel

1. Abra a **App Store** no Umbrel.
2. Clique nos três pontinhos (canto superior direito) → **Community App Stores**.
3. Cole a URL `https://github.com/edu-ricardo/florencio-store` e clique em **Add**.

## Aplicativos disponíveis

| App | Porta | Observações |
| --- | --- | --- |
| **Agent DVR** | 8190 | Vigilância por vídeo. Usa também 3478 (TCP/UDP) e 50000-50010/UDP para WebRTC. |
| **BookOrbit** | 8745 | Biblioteca de ebooks/audiobooks/quadrinhos. Os livros ficam em `Downloads/books` no app Files. No primeiro acesso, use a senha exibida pelo Umbrel como *Setup token*. |

## Regras para adicionar novos apps

- A pasta e o `id` do app devem começar com `florencio-store-`.
- No `docker-compose.yml`, o `app_proxy` **não** deve ter `image:`; o `APP_HOST` segue o formato `<app-id>_<serviço>_1`.
- `port` no `umbrel-app.yml` é a porta externa (única no Umbrel); `APP_PORT` é a porta interna do container.
- `icon` precisa ser uma URL pública (ex.: raw.githubusercontent.com).

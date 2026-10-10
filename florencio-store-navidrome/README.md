# Navidrome (HD externo)

Servidor de streaming de música (API Subsonic) lendo a biblioteca do HD externo.
Versão fixa **0.64.2**, imagem `deluan/navidrome`.

## Endereços

| Para quê | Endereço |
| --- | --- |
| Abrir no navegador (rede local) | `http://umbrel.local:8808` |
| Outro container ou túnel Cloudflare (DockFlare, cloudflared) | **`http://florencio-store-navidrome_server_1:4533`** |
| Apps Subsonic (Symfonium, DSub, Feishin...) | a URL pública do túnel, com o usuário e a senha do Navidrome |

A porta 8808 é só a da página do Umbrel. Ela é diferente da 4533 do app oficial para que os dois possam estar instalados juntos; a porta interna continua 4533.

## O que ele enxerga no HD

| No HD | No container | Acesso |
| --- | --- | --- |
| `<HD>/musica/biblioteca` | `/music` | somente leitura |
| *(disco do sistema)* `app-data/florencio-store-navidrome/data` | `/data` | banco, cache e capas |

O `exports.sh` usa o HD que tem uma pasta `musica` na raiz (o umbrelOS monta cada HD em `/home/umbrel/umbrel/external/<nome do HD>`). **Se nenhum tem e há exatamente um HD montado, ele cria a `musica` nesse HD**; com dois ou mais HDs, não adivinha: crie a pasta `musica` no HD certo. Cria também as subpastas que faltarem. Se o HD estiver desconectado, o app **não sobe** (de propósito), em vez de criar uma biblioteca vazia no disco do sistema.

Configuração aplicada: `ND_SCANSCHEDULE=15m`, `ND_ENABLETRANSCODINGCONFIG=true`, `ND_PLAYLISTSPATH=.`.

> **Playlists:** com `ND_PLAYLISTSPATH=.` o Navidrome procura arquivos `.m3u` dentro da própria `biblioteca`. A pasta `<HD>/musica/playlists` **não é lida** por este app.

## Segurança: login do Umbrel desligado

`PROXY_AUTH_ADD: "false"` tira a tela de login do Umbrel da frente do app. Isso é necessário para os apps Subsonic funcionarem, mas significa que **a única proteção é o login do próprio Navidrome**:

- No primeiro acesso o Navidrome deixa **quem chegar primeiro** criar a conta de administrador. Crie a sua antes de publicar o app na internet.
- Use uma senha forte e crie um usuário comum para o uso diário. O Navidrome não tem verificação em duas etapas.
- Se for expor pelo Cloudflare Tunnel, uma política do Cloudflare Access na frente quebra os apps Subsonic, a menos que você use um *service token* neles.

## Versão oficial do Umbrel

O Navidrome da App Store oficial lê `Downloads/music` do disco do sistema, e o volume dele não pode ser trocado sem editar os arquivos do app (a edição some a cada atualização). Por isso este app existe. Dá para ter os dois instalados; só um é necessário.

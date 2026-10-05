# Florencio Store

Loja de comunidade (Community App Store) para o umbrelOS.

## Como instalar no seu Umbrel

1. Abra a **App Store** no Umbrel.
2. Clique nos três pontinhos (canto superior direito) → **Community App Stores**.
3. Cole a URL `https://github.com/edu-ricardo/florencio-store` e clique em **Add**.

## Aplicativos disponíveis

| App | Porta | Observações |
| --- | --- | --- |
| **Agent DVR** | 8747 | Vigilância por vídeo. Usa também 3478 (TCP/UDP) e 50000-50010/UDP para WebRTC. |
| **BookOrbit** | 8746 | Biblioteca de ebooks/audiobooks/quadrinhos. Os livros ficam em `Downloads/books` no app Files. No primeiro acesso, use a senha exibida pelo Umbrel como *Setup token*. |
| **Prometheus** | 9095 | Fonte de dados para o Grafana. Já coleta métricas do host (node-exporter, porta 9100) e de cada app (cAdvisor). No Grafana use a URL `http://florencio-store-prometheus_server_1:9090`. |
| **Listenarr** | 4545 | Gerenciador automático de audiobooks (estilo Sonarr). Use `/downloads/books/audiobooks` como Root Folder para aparecerem no BookOrbit. |
| **Bookshelf** | 8790 | Substituto do Readarr (fork com metadados do Hardcover) para ebooks. Root Folder sugerido: `/downloads/books/ebooks`. |
| **Chaptarr** | 8791 | Sucessor do Readarr (beta) com audiobooks e ebooks na mesma instância. |
| **openGym** | 8792 | Treinos e peso corporal. Login por passkey exige HTTPS (Tailscale/Cloudflare); pela rede local use "Continuar sem conta". Configuração em `app-data/florencio-store-opengym/data/opengym.env`. |
| **Libreseerr** | 8794 | Pedidos de livros/audiobooks (estilo Seerr) integrado ao Bookshelf e Chaptarr. Login inicial `admin`/`admin`. Só x86 (não roda em Raspberry Pi). |
| **LAN Orangutan** | 291 | Descoberta de aparelhos na rede. Usa a rede do host; senha criada no primeiro acesso. |
| **Jellydash** | 8795 | Painel estilo Tautulli para o Jellyfin. Coloque a chave de API em `app-data/florencio-store-jellydash/data/jellydash.env`. |
| **Scrypted** | 11080 | Câmeras no HomeKit/Google Home/Alexa. Usa a rede do host (HTTPS na 10453). |
| **Obsidian LiveSync** | 5984 | Servidor CouchDB para o plugin Self-hosted LiveSync. No celular o Obsidian exige HTTPS (Tailscale/Cloudflare). |
| **Marreta** | 8796 | Remove paywall de notícias. Painel `/admin` com `admin@marreta.local` e a senha do Umbrel. |
| **Shelfmark** | 8797 | Busca unificada de livros/audiobooks (web, torrent, usenet, IRC). Salva em `Downloads/books/shelfmark` (dentro do BookOrbit). Precisa de ~2 GB de RAM. |
| **Kavita** | 8798 | Servidor de leitura para mangá, HQs e livros, com OPDS. Bibliotecas em `/downloads/...` (pasta Downloads do Files). |
| **DockFlare** | 8799 | Publica apps do Umbrel no seu domínio pelo Cloudflare Tunnel (sem abrir portas). Precisa de domínio na Cloudflare e token de API. |
| **Destinos dos Apps** | 8800 | Tabela com o endereço interno (`container:porta`) de cada app instalado, para usar no Cloudflare Tunnel/DockFlare. |
| **Vamos Jogar** | 8801 | Organização de jogatinas de tabuleiro com os amigos, com banco e login próprios (PocketBase; só x86). Antes de instalar ou atualizar, crie `data/pocketbase.env` e preencha `data/api.env` em `app-data/florencio-store-vamos-jogar/`. O login com Google só funciona pelo domínio público (`https://vamosjogar.eduhomelab.monster`), não pelo ícone do Umbrel (`http://umbrel.local:8801`). |
| **Whisparr v3** | 8802 | Whisparr v3 (Eros, alpha) para conteúdo adulto, estilo Sonarr. Root Folder sugerido: `/downloads/whisparr`. No Prowlarr adicione como "Whisparr" (`http://florencio-store-whisparr-v3_server_1:6969`). Não aproveita a biblioteca do v2. |
| **Vamos Jogar (homologação)** | 8804 | Ensaio da migração do Vamos Jogar para o PocketBase, separado do app em uso (só x86). Preencha `data/pocketbase.env` e `data/api.env` em `app-data/florencio-store-vamos-jogar-homolog/` e reinicie o app. |
| **Filestash** | 8803 | Gerenciador de arquivos web para os arquivos do Umbrel e SFTP, S3, WebDAV, SMB, Drive... Senha de admin em `/admin`; arquivos do Umbrel pelo backend *Local* em `/umbrel`. |

## Regras para adicionar novos apps

- A pasta e o `id` do app devem começar com `florencio-store-`.
- No `docker-compose.yml`, o `app_proxy` **não** deve ter `image:`; o `APP_HOST` segue o formato `<app-id>_<serviço>_1`.
- `port` no `umbrel-app.yml` é a porta externa e não pode repetir a de nenhum app oficial (confira em [getumbrel/umbrel-apps](https://github.com/getumbrel/umbrel-apps)); `APP_PORT` é a porta interna do container.
- `icon` precisa ser uma URL pública (ex.: raw.githubusercontent.com).

## Atualizações automáticas

O workflow [`check-app-updates.yml`](.github/workflows/check-app-updates.yml) roda nos dias 1 e 15 de cada mês (e manualmente em **Actions → Verificar atualizações dos apps → Run workflow**). Ele usa [`scripts/check_updates.py`](scripts/check_updates.py) para procurar versões novas de cada imagem, com o mesmo formato de tag da atual, e abre (ou atualiza) um Pull Request no branch `auto/app-updates` com a imagem, o digest e a versão do app já trocados. O Umbrel só oferece a atualização depois do merge.

- Tags sem número de versão (`nightly`, `pg18`) não são verificadas.
- Quando sai uma versão nova do openGym, a imagem `coach` é compilada antes do PR.
- Para o workflow conseguir abrir o PR, ative em **Settings → Actions → General → Workflow permissions** a opção **Allow GitHub Actions to create and approve pull requests**. Sem ela, ele abre uma issue com o link do branch.

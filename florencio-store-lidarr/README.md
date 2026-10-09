# Lidarr (HD externo)

Gerenciador de coleção de músicas com a biblioteca no HD externo.
Versão fixa **3.1.0**, imagem `linuxserver/lidarr`.

## Endereços

| Para quê | Endereço |
| --- | --- |
| Abrir no navegador (rede local) | `http://umbrel.local:8809` |
| Prowlarr, Soularr, túnel Cloudflare | **`http://florencio-store-lidarr_server_1:8686`** |

A porta 8809 é só a da página do Umbrel (diferente da 8686 do Lidarr oficial, para os dois poderem estar instalados juntos). A porta interna continua 8686.

## O que ele enxerga

| Onde | No container | Para quê |
| --- | --- | --- |
| `<HD>/musica` (inteiro) | `/musica` | biblioteca em `/musica/biblioteca`, downloads do slskd em `/musica/slskd/downloads` |
| *(disco do sistema)* `app-data/florencio-store-lidarr/data/config` | `/config` | configuração e banco |
| Downloads do Umbrel (app Files) | `/downloads` | só para o Transmission; pode ignorar se não usar torrent |

Biblioteca e downloads ficam no **mesmo volume**, então a importação **move** os arquivos em vez de copiar. No exFAT/NTFS não existe hardlink; não precisa dele para isso.

O `exports.sh` procura o HD que tem uma pasta `musica` na raiz e cria as subpastas. Sem o HD, o app **não sobe** (de propósito), em vez de gravar música no disco do sistema.

## Configurar depois de instalar

1. **Criar usuário e senha** (Settings > General > Security, se o Lidarr não pedir sozinho). O login está sempre obrigatório.
2. **Root folder:** Settings > Media Management > Root Folders > `/musica/biblioteca`.
3. **Prowlarr** (app oficial) > Settings > Apps > Add > Lidarr:
   - Prowlarr Server: `http://prowlarr_server_1:9696`
   - Lidarr Server: `http://florencio-store-lidarr_server_1:8686`
   - API Key: a do Lidarr (Settings > General).
4. **Transmission** (opcional, para torrents): Settings > Download Clients > Transmission, host `transmission_server_1`, porta `9091`.
5. **Soularr** (app `florencio-store-slskd`): usa a API key do Lidarr. Veja o README dele.

## Segurança: login do Umbrel desligado

`PROXY_AUTH_ADD: "false"` tira a tela de login do Umbrel da frente do app (Prowlarr e Soularr falam com o Lidarr pela API). Por isso o compose força o login do Lidarr (`LIDARR__AUTH__METHOD=Forms` e `LIDARR__AUTH__REQUIRED=Enabled`): **um Lidarr novo vem sem autenticação nenhuma**, e sem isso qualquer pessoa que alcançasse a porta seria administradora.

- Crie o usuário **antes** de publicar o app pelo túnel.
- A chave de API do Lidarr funciona sem login. Não a divulgue.
- Como o login vem de variável de ambiente, o método de autenticação fica bloqueado na tela de configurações.

## Por que não usa `user: "1000:1000"`

A imagem `linuxserver` precisa começar como root e trocar para o usuário definido em `PUID`/`PGID` (o Lidarr oficial do Umbrel faz o mesmo). Só `/config` tem o dono alterado; o HD (`/musica`) não é tocado, então não há `chown` no exFAT/NTFS.

## Lidarr oficial do Umbrel

O Lidarr da App Store oficial (porta 8686) monta só `Downloads` do disco do sistema e usa um configurador automático; trocar o volume dele para o HD exigiria editar os arquivos do app, e a edição some a cada atualização. Por isso este existe. Dá para ter os dois instalados (portas, containers e dados são separados), mas **são duas instalações do Lidarr com bancos independentes**: só um é necessário.

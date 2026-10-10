# slskd + Soularr

Cliente Soulseek (slskd) e o Soularr, que liga o slskd ao Lidarr, **no mesmo app** para dividirem rede e volumes.
Versões fixas: **slskd 0.26.0** (`slskd/slskd`) e **Soularr v1.2.2** (`mrusse08/soularr`).

## Endereços

| Para quê | Endereço |
| --- | --- |
| slskd no navegador | `http://umbrel.local:8810` (usuário `admin`, senha mostrada pelo Umbrel) |
| slskd, de outro container ou do túnel | **`http://florencio-store-slskd_slskd_1:5030`** |
| Soularr (interface web, **sem login**) | `http://umbrel.local:8265` |
| Soularr, de outro container | `florencio-store-slskd_soularr_1` |
| Soulseek (conexões de outros usuários) | porta **50300/TCP** do Umbrel |
| slskd em HTTPS | `https://umbrel.local:5031` (certificado autoassinado) |

## O que eles enxergam no HD

| No HD | slskd | Soularr |
| --- | --- | --- |
| `<HD>/musica` (inteiro) | `/musica` | — |
| `<HD>/musica/slskd/downloads` | `SLSKD_DOWNLOADS_DIR=/musica/slskd/downloads` | `/downloads` |
| `<HD>/musica/slskd/incompletos` | `SLSKD_INCOMPLETE_DIR=/musica/slskd/incompletos` | — |
| `<HD>/musica/biblioteca` | `SLSKD_SHARED_DIR=/musica/biblioteca` (compartilhada no Soulseek) | — |

A configuração do slskd (`slskd.yml`) e a do Soularr (`config.ini`) ficam no **disco do sistema**, em `app-data/florencio-store-slskd/data/slskd` e `.../data/soularr`. O `exports.sh` usa o HD que tem uma pasta `musica` na raiz. **Se nenhum tem e há exatamente um HD montado, ele cria a `musica` nesse HD**; com dois ou mais HDs, não adivinha: crie a pasta `musica` no HD certo. Cria também as subpastas. Sem o HD o app **não sobe** (de propósito), em vez de baixar músicas para o disco do sistema.

## 1. Abrir a porta no roteador (obrigatório para o Soulseek)

O Soulseek precisa que **50300/TCP** esteja acessível de fora. No roteador, redirecione:

| Protocolo | Porta externa | Porta interna | IP de destino |
| --- | --- | --- | --- |
| TCP | 50300 | 50300 | `192.168.68.117` (o IP do seu Umbrel) |

Reserve esse IP no roteador (DHCP fixo), senão o redirecionamento quebra se ele mudar. Sem a porta aberta o slskd ainda funciona, mas só consegue baixar de quem aceita conexão dele.

## 2. Configurar o slskd

1. Entre em `http://umbrel.local:8810` com `admin` e a senha do Umbrel.
2. Em **System > Options**, preencha a sua conta do Soulseek (`soulseek.username` e `soulseek.password`; crie uma gratuitamente se não tiver) e salve (`slskd` reinicia).
3. Crie a chave de API do Soularr, ainda em **Options** (editor de YAML):

```yaml
web:
  authentication:
    api_keys:
      soularr:
        key: COLOQUE-UMA-CHAVE-DE-16-A-255-CARACTERES
        role: readwrite
        cidr: 0.0.0.0/0,::/0
```

Guarde essa chave: ela vai no `config.ini` do Soularr.

## 3. Colar as chaves no Soularr

O Soularr `v1.2.2` **não cria o `config.ini` sozinho**: sem o arquivo ele só registra o erro e sai. Por isso o app já vem com um `config.ini` pronto, baseado no modelo oficial, com os endereços e as pastas certos. Falta só trocar os dois `COLE-AQUI...` pelas chaves de API, pela interface em `http://umbrel.local:8265` (Config) ou direto em `app-data/florencio-store-slskd/data/soularr/config.ini`:

```ini
[Lidarr]
api_key = <chave do Lidarr: Settings > General>
host_url = http://florencio-store-lidarr_server_1:8686
download_dir = /musica/slskd/downloads

[Slskd]
api_key = <a chave "soularr" criada no passo 2>
host_url = http://florencio-store-slskd_slskd_1:5030
url_base = /
download_dir = /downloads
```

`download_dir` do `[Lidarr]` é o caminho **como o Lidarr enxerga** a pasta; o do `[Slskd]` é **como o Soularr enxerga** (`/downloads`). Reinicie o app depois de editar. Enquanto as chaves forem as de exemplo, o Soularr só registra erros no log; é normal.

> O `config.ini` só é copiado na **instalação**; atualizações do app não o sobrescrevem, então as suas chaves ficam.

## Segurança: login do Umbrel desligado

- **slskd:** `PROXY_AUTH_ADD: "false"`. Sem o login do Umbrel, a única proteção é o login do próprio slskd. O compose **substitui o padrão `slskd`/`slskd`** por `admin` e a senha do Umbrel. Como a senha vem de variável de ambiente, ela não é trocada pela interface do slskd. A chave de API do passo 2 funciona sem login: não a divulgue.
- **Soularr (porta 8265): não tem nenhum login** e mostra e edita o `config.ini`, que contém as chaves de API do Lidarr e do slskd. Ele é publicado direto na porta, sem `app_proxy`. **Não o exponha pelo túnel Cloudflare** e não abra a 8265 no roteador. Qualquer aparelho da sua rede local consegue abri-lo.
- **Compartilhar a biblioteca** no Soulseek (`/musica/biblioteca`) é decisão sua e responsabilidade sua.
- O Soulseek expõe o seu IP aos outros usuários (é uma rede ponto a ponto).

## Dependências

Este app **não declara `dependencies`**: ele funciona sozinho, e o Soularr só passa a trabalhar quando o Lidarr existe. Por isso a ordem de instalação é livre (o Soularr tenta de novo a cada 5 minutos). Prowlarr e Transmission são do Lidarr, não deste app.

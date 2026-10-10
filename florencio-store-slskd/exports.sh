# Pasta "musica" do HD externo, compartilhada pelos apps de música da loja
# (florencio-store-navidrome, florencio-store-lidarr, florencio-store-slskd).
# O bloco abaixo é igual nos três apps: eles precisam enxergar o MESMO volume
# para o Lidarr importar movendo os arquivos em vez de copiar.
#
# O umbrelOS monta cada HD externo em ${UMBREL_ROOT}/external/<nome do HD>
# (no Umbrel: /home/umbrel/umbrel/external/<nome do HD>). O nome do HD não fica
# escrito aqui:
#   1. usa o primeiro HD que já tem uma pasta "musica" na raiz;
#   2. se nenhum tem e existe exatamente UM HD montado, cria a pasta "musica" nele;
#   3. com dois ou mais HDs sem "musica", não adivinha: crie a pasta no HD certo.

FLORENCIO_MUSICA_DIR=""
for florencio_candidate in "${UMBREL_ROOT}"/external/*/musica; do
	if [[ -d "${florencio_candidate}" ]]; then
		FLORENCIO_MUSICA_DIR="${florencio_candidate}"
		break
	fi
done

if [[ -z "${FLORENCIO_MUSICA_DIR}" ]]; then
	# "Montado de verdade" = outro dispositivo que a pasta "external". Uma pasta
	# solta no disco do sistema não conta, para nunca criar a biblioteca lá.
	florencio_external_dev="$(stat -c %d "${UMBREL_ROOT}/external" 2>/dev/null || true)"
	florencio_drives=()
	for florencio_drive in "${UMBREL_ROOT}"/external/*/; do
		florencio_drive="${florencio_drive%/}"
		if [[ -d "${florencio_drive}" && -n "${florencio_external_dev}" && "$(stat -c %d "${florencio_drive}" 2>/dev/null || true)" != "${florencio_external_dev}" ]]; then
			florencio_drives+=("${florencio_drive}")
		fi
	done
	if [[ "${#florencio_drives[@]}" -eq 1 ]]; then
		if mkdir -p "${florencio_drives[0]}/musica" 2>/dev/null; then
			FLORENCIO_MUSICA_DIR="${florencio_drives[0]}/musica"
		fi
	fi
fi

if [[ -n "${FLORENCIO_MUSICA_DIR}" ]]; then
	# Cria o que faltar (não mexe no que já existe). O chown só importa em HD
	# ext4; em exFAT/NTFS o umbrelOS já monta o HD com o dono certo e o chown
	# é ignorado.
	for florencio_sub in biblioteca playlists slskd/downloads slskd/incompletos; do
		mkdir -p "${FLORENCIO_MUSICA_DIR}/${florencio_sub}" 2>/dev/null || true
	done
	chown 1000:1000 "${FLORENCIO_MUSICA_DIR}" "${FLORENCIO_MUSICA_DIR}"/biblioteca "${FLORENCIO_MUSICA_DIR}"/playlists "${FLORENCIO_MUSICA_DIR}"/slskd "${FLORENCIO_MUSICA_DIR}"/slskd/downloads "${FLORENCIO_MUSICA_DIR}"/slskd/incompletos 2>/dev/null || true
else
	# Nenhum HD montado, ou mais de um sem a pasta "musica". O caminho abaixo não
	# existe de propósito: o compose usa create_host_path: false, então o app
	# falha ao subir com este nome no erro, em vez de gravar música no disco do
	# sistema. Conecte o HD, ou crie a pasta "musica" na raiz do HD certo.
	FLORENCIO_MUSICA_DIR="${UMBREL_ROOT}/external/HD-NAO-ENCONTRADO-crie-a-pasta-musica-na-raiz-do-HD/musica"
fi

export FLORENCIO_MUSICA_DIR
unset florencio_candidate florencio_sub florencio_drive florencio_drives florencio_external_dev

# --- Só deste app --------------------------------------------------------------
# slskd e Soularr rodam como 1000:1000 e gravam em app-data (disco do sistema).
# O config.ini do Soularr é copiado na instalação, possivelmente como root, e o
# Soularr precisa poder editá-lo pela interface web. Sem -R de propósito.
florencio_app_dir="${EXPORTS_APP_DIR:-${UMBREL_ROOT}/app-data/florencio-store-slskd}"
chown 1000:1000 "${florencio_app_dir}/data/slskd" "${florencio_app_dir}/data/soularr" "${florencio_app_dir}/data/soularr/config.ini" 2>/dev/null || true
unset florencio_app_dir

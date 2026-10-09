# Pasta "musica" do HD externo, compartilhada pelos apps de música da loja
# (florencio-store-navidrome, florencio-store-lidarr, florencio-store-slskd).
# O bloco abaixo é igual nos três apps: os apps precisam enxergar o MESMO volume para
# o Lidarr importar movendo os arquivos em vez de copiar.
#
# O umbrelOS monta cada HD externo em ${UMBREL_ROOT}/external/<nome do HD>
# (no Umbrel: /home/umbrel/umbrel/external/<nome do HD>). O nome do HD não fica
# escrito aqui: usamos o primeiro HD que tiver uma pasta "musica" na raiz.
# Para começar, crie a pasta "musica" na raiz do HD (app Files > External).

FLORENCIO_MUSICA_DIR=""
for florencio_candidate in "${UMBREL_ROOT}"/external/*/musica; do
	if [[ -d "${florencio_candidate}" ]]; then
		FLORENCIO_MUSICA_DIR="${florencio_candidate}"
		break
	fi
done

if [[ -n "${FLORENCIO_MUSICA_DIR}" ]]; then
	# Cria o que faltar (não mexe no que já existe). O chown só importa em HD
	# ext4; em exFAT/NTFS o umbrelOS já monta o HD com o dono certo e o chown
	# é ignorado.
	for florencio_sub in biblioteca playlists slskd/downloads slskd/incompletos; do
		mkdir -p "${FLORENCIO_MUSICA_DIR}/${florencio_sub}" 2>/dev/null || true
	done
	chown 1000:1000 "${FLORENCIO_MUSICA_DIR}" "${FLORENCIO_MUSICA_DIR}"/biblioteca "${FLORENCIO_MUSICA_DIR}"/playlists "${FLORENCIO_MUSICA_DIR}"/slskd "${FLORENCIO_MUSICA_DIR}"/slskd/downloads "${FLORENCIO_MUSICA_DIR}"/slskd/incompletos 2>/dev/null || true
else
	# HD desconectado ou sem a pasta "musica". O caminho abaixo não existe de
	# propósito: o compose usa create_host_path: false, então o app falha ao
	# subir com um erro claro em vez de gravar música no disco do sistema.
	FLORENCIO_MUSICA_DIR="${UMBREL_ROOT}/external/HD-NAO-ENCONTRADO/musica"
fi

export FLORENCIO_MUSICA_DIR
unset florencio_candidate florencio_sub

# --- Só deste app --------------------------------------------------------------
# slskd e Soularr rodam como 1000:1000 e gravam em app-data (disco do sistema).
# O config.ini do Soularr é copiado na instalação, possivelmente como root, e o
# Soularr precisa poder editá-lo pela interface web. Sem -R de propósito.
chown 1000:1000 "${EXPORTS_APP_DIR}/data/slskd" "${EXPORTS_APP_DIR}/data/soularr" "${EXPORTS_APP_DIR}/data/soularr/config.ini" 2>/dev/null || true

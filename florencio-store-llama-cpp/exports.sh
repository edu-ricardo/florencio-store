# Cria Downloads/llama.cpp com o dono do Umbrel, para o app Files conseguir enviar modelos
mkdir -p "${UMBREL_ROOT}/data/storage/downloads/llama.cpp" 2>/dev/null || true
chown 1000:1000 "${UMBREL_ROOT}/data/storage/downloads/llama.cpp" 2>/dev/null || true

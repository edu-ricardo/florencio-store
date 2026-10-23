# A Dark Room não publica imagem oficial: é um site estático (index.html +
# css/script/lib/img/audio/lang, sem build nem backend). Essa imagem só
# serve os arquivos do próprio repositório com o nginx.
FROM nginx:1.27-alpine
COPY . /usr/share/nginx/html

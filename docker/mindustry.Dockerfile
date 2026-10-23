# As imagens Docker comunitárias do Mindustry ficaram desatualizadas: a
# anderpuqing/mindustry embute um JRE 11 fixo, mas o Mindustry (a partir da
# v159) exige Java 17+, e dá UnsupportedClassVersionError. Essa imagem baixa
# o .jar oficial da versão pedida e usa um JRE atual.
ARG VERSION
FROM eclipse-temurin:21-jre-alpine
ARG VERSION
RUN wget -q "https://github.com/Anuken/Mindustry/releases/download/v${VERSION}/server-release.jar" -O /server-release.jar
WORKDIR /mindustry
RUN mv /server-release.jar server-release.jar
VOLUME /mindustry/config
EXPOSE 6567/tcp 6567/udp
ENTRYPOINT ["java", "-jar", "server-release.jar"]

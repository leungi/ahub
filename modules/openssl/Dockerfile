FROM alpine:3.1

RUN apk update && \
  apk add --no-cache openssl && \
  rm -rf /var/cache/apk/*

ENTRYPOINT ["openssl", "req", "-batch", "-x509", "-nodes", "-days", "365", "-newkey", "rsa:2048"]

CMD ["-keyout", "/var/server.key", "-out", "/var/server.crt"]

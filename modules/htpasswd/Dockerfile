FROM alpine:3.1

RUN apk add --update apache2-utils

ENTRYPOINT ["htpasswd", "-c", "-b", "/var/.htpasswd"]
CMD ["username", "password"]

param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_certbot:$tag ./modules/certbot
docker push qunis/ahub_certbot:$tag


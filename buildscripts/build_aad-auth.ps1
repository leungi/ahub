
param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_aad-auth:$tag ./modules/aad-auth
docker push qunis/ahub_aad-auth:$tag


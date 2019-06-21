
param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_aadauth:$tag ./modules/aadauth
docker push qunis/ahub_aadauth:$tag


param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_artillery:$tag ./modules/artillery
docker push qunis/ahub_artillery:$tag

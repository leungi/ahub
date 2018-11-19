param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_boss:$tag ./modules/boss
docker push qunis/ahub_boss:$tag


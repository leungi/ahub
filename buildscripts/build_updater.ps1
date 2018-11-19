
param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_updater:$tag ./modules/updater
docker push qunis/ahub_updater:$tag


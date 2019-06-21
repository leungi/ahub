
param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_scheduler:$tag ./modules/scheduler
docker push qunis/ahub_scheduler:$tag


param (
    [string]$tag = "latest"
)
docker build -t qunis/ahub_rnode:$tag ./modules/rnode
docker push qunis/ahub_rnode:$tag


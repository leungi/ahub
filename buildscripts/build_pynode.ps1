param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_pynode:$tag ./modules/pynode
docker push qunis/ahub_pynode:$tag

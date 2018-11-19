param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_nginx ./modules/nginx
docker push qunis/ahub_nginx


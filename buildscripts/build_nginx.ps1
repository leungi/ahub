# build all images and push to registry

docker build -t qunis/ahub_nginx ../modules/nginx
docker push qunis/ahub_nginx


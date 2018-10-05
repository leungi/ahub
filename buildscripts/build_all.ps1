# build all images and push to registry

docker build -t qunis/ahub_rnode ../modules/rnode
docker push qunis/ahub_rnode

docker build -t qunis/ahub_nginx ../modules/nginx
docker push qunis/ahub_nginx

docker build -t qunis/ahub_client ../modules/client
docker push qunis/ahub_client

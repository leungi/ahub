# build all images and push to registry

docker build -t qunis/ahub_node ../modules/node
docker push qunis/ahub_node

docker build -t qunis/ahub_nginx ../modules/nginx
docker push qunis/ahub_nginx

docker build -t qunis/ahub_rclient ../modules/rclient
docker push qunis/ahub_rclient

docker stack deploy -c .\docker-compose.yml ahub
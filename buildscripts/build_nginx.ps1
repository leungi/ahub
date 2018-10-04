# build all images and push to registry

docker build -t qunis/qaf_nginx ./nginx
docker push qunis/qaf_nginx

docker stack deploy -c .\docker-compose.yml qaf
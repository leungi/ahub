# build all images and push to registry
docker stack rm qaf

docker build -t qunis/qaf_boss ./boss
docker push qunis/qaf_boss

docker stack deploy -c .\docker-compose.yml qaf
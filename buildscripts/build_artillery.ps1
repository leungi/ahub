# build all images and push to registry
docker stack rm qaf

docker build -t qunis/qaf_artillery ./artillery
docker push qunis/qaf_artillery

docker stack deploy -c .\docker-compose.yml qaf
# build all images and push to registry
docker stack rm qaf

docker build -t qunis/qaf_node ./node
docker push qunis/qaf_node

docker stack deploy -c .\docker-compose.yml qaf
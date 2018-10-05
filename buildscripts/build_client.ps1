# build all images and push to registry

docker build -t qunis/ahub_client ../modules/client
docker push qunis/ahub_client

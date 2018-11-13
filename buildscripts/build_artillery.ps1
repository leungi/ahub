# build all images and push to registry

docker build -t qunis/ahub_artillery ./modules/artillery
docker push qunis/ahub_artillery

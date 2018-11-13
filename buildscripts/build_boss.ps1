# build all images and push to registry

docker build -t qunis/ahub_boss ./modules/boss
docker push qunis/ahub_boss


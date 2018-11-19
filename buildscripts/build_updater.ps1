# build all images and push to registry

docker build -t qunis/ahub_updater ./modules/updater
docker push qunis/ahub_updater


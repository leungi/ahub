# build all images and push to registry

docker build -t qunis/ahub_gui ./modules/gui
docker push qunis/ahub_gui

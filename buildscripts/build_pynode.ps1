# build all images and push to registry

docker build -t qunis/ahub_pynode ./modules/pynode
docker push qunis/ahub_pynode

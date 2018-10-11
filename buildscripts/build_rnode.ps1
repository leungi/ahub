# build all images and push to registry

docker build -t qunis/ahub_rnode ../modules/rnode
docker push qunis/ahub_rnode


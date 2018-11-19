param (
    [string]$tag = "latest"
)

docker build -t qunis/ahub_gui:$tag ./modules/gui
docker push qunis/ahub_gui:$tag

param (
    [string]$tag = "latest"
)

$lwd = $pwd

cd ./modules/reactgui
npm run-script build
Copy-Item ./Dockerfile -destination .\build\Dockerfile
cd $lwd


docker build -t qunis/ahub_reactgui:$tag ./modules/reactgui/build/.
docker push qunis/ahub_reactgui:$tag

param (
    [string]$tag = "latest"
)

./buildscripts/build_rnode.ps1 -tag $tag
./buildscripts/build_pynode.ps1 -tag $tag
./buildscripts/build_boss.ps1 -tag $tag
./buildscripts/build_reactgui.ps1 -tag $tag
./buildscripts/build_scheduler.ps1 -tag $tag
./buildscripts/build_aadauth.ps1 -tag $tag
./buildscripts/build_certbot.ps1 -tag $tag
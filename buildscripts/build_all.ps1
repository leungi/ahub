param (
    [string]$tag = "latest"
)

./buildscripts/build_rnode.ps1 -tag $tag
./buildscripts/build_pynode.ps1 -tag $tag
./buildscripts/build_boss.ps1 -tag $tag
./buildscripts/build_gui.ps1 -tag $tag
./buildscripts/build_updater.ps1 -tag $tag
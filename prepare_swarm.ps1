docker-machine --native-ssh create -d hyperv --hyperv-virtual-switch "myswitch" myvm1
docker-machine --native-ssh create -d hyperv --hyperv-virtual-switch "myswitch" myvm2

docker-machine --native-ssh ssh myvm1 "docker swarm init --advertise-addr 192.168.137.24"
docker-machine --native-ssh ssh myvm2 "docker swarm join --token SWMTKN-1-1i5pxjvexl7dei4464sz13nfl09gd84xyuvk6xmx6t38b8diyx-9uhd8vsv8ay1d50ro6v38vmhc 192.168.137.24:2377"

docker-machine --native-ssh ssh myvm1 "docker node ls"
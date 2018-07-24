
#docker-machine --native-ssh env myvm1
& "C:\Program Files\Docker\Docker\Resources\bin\docker-machine.exe" --native-ssh env myvm1 | Invoke-Expression

docker stack deploy -c docker-compose_swarm.yml qaf
# HOW TO DEPLOY TO AZURE CONTAINER SERVICE

When creating the container service you need to provide a public RSA key. This is created with

```
ssh-keygen
```

The file is created at ```~/.ssh/id_rsa.pub``` per default. The contents need to be copypasted to the Azure dialogue.

The private key needs to be added to the local keyring via

```
ssh-add ~/.ssh/id_rsa
```


Then you need to login to the manager VM and do the upgrade to Ubuntu 16.04

```
ssh ahubadmin@ahubmgmt.westeurope.cloudapp.azure.com
do-release-upgrade
```

After that, the docker version needs to be updated as well. Please follow the instructions on:
https://docs.docker.com/install/linux/docker-ce/ubuntu/#set-up-the-repository



commands to update to latest swarm version

```

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock nexdrew/rekcod containers_swarm_1

docker update --restart=no containers_swarm_1
docker stop containers_swarm_1
docker container prune -f

docker run --name containers_swarm_1 -v /etc/docker:/etc/docker:rw -p 2375:2375/tcp --link containers_consul_1:consul --link containers_consul_1:consul_1 --link containers_consul_1:containers_consul_1 --restart always -h a36b30cc1691 --expose 2375/tcp -e 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' -e 'SWARM_HOST=:2375' -d --entrypoint "/swarm" swarm:latest manage --replication --advertise 172.16.0.5:2375 --discovery-opt kv.path=docker/nodes consul://172.16.0.5:8500
```

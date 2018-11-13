# VM configuration

## ahubmaster


### install docker
```bash
sudo apt-get update && \
    sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
    sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable" && \
   sudo apt-get update && \
   sudo apt-get install -y docker-ce 
   
```

### add user to docker group
need to relogin to take effect
```bash
sudo addgroup ahubadmin docker
```

### install certbot for certificates
```bash
sudo add-apt-repository ppa:certbot/certbot && \
    sudo apt-get update && \
    sudo apt-get install -y python-certbot-apache
```

This creates the certificate
```bash
sudo certbot certonly --apache -n \
    -d ahub.westeurope.cloudapp.azure.com \
    -m martin.hanewald@qunis.de --agree-tos
```

### disable apache
```bash
sudo systemctl stop apache2.service
sudo systemctl disable apache2.service
```

### create redisdata folder
```bash
sudo mkdir /redisdata
sudo chown root:docker /redisdata

```


### ports to free

* 80: HTTP
* 433: HTTPS
* 22: SSH
* 8080: Visualizer
* 9000: portainer
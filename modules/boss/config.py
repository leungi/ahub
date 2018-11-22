# Main config for AHUB Boss

BOSSPORT = 8000
REDISHOST = "redis"
DOCKERHOST = 'unix://var/run/docker.sock'
NGINXHOST = 'nginx'

DEBUGHOST = 'ahub.westeurope.cloudapp.azure.com'

# to let the get-service function know, which nodes it does not need to check
AHUBSTACK = ['boss', 'gui', 'portainer', 'redis', 'nginx', 'updater', 'aad-auth']

# Configure Swagger
SWAGGER = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'swagger',
            "route": '/swagger.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/__swagger__/"
}

CERTHOST = 'ahub.westeurope.cloudapp.azure.com'
CERTEMAIL = 'martin.hanewald@qunis.de'

PORT = 8000

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

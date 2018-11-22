from flasgger import Swagger
from flask import Flask, Response
from flask_cors import CORS
import json
import os

# local imports
import config


CERTBOTCMD = f'certbot certonly --standalone -n \
    -d {config.CERTHOST} \
    -m {config.CERTEMAIL} --agree-tos'

# ----------------------------------------------------------
# FLASK
# ----------------------------------------------------------

# init Flask and set JSON as default response
#class JSONResponse(Response):
#    default_mimetype = 'application/json'


app = Flask(__name__)

CORS(app)  # activate CORS
#app.response_class = JSONResponse
swagger = Swagger(app, config=config.SWAGGER)


# ----------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------


@app.route("/renew_certificate")
def new_certificate():
    """new_certificate
        ---
        parameters: []
        """
    ans = os.popen(CERTBOTCMD).read()
    return ans


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)

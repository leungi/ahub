from flasgger import Swagger
from flask import Flask, request
from flask_cors import CORS
import yaml
import os
import re
import json


with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(format(exc))


# ----------------------------------------------------------
# FLASK
# ----------------------------------------------------------

# init Flask and set JSON as default response
#class JSONResponse(Response):
#    default_mimetype = 'application/json'
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
    "specs_route": "/__swagger__/"}

app = Flask(__name__)

CORS(app)  # activate CORS
#app.response_class = JSONResponse
swagger = Swagger(app, config=SWAGGER)


# ----------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------



@app.route("/openssl")
def openssl():
    """new_certificate
        ---
        parameters: []
        """
    OPENSSLCMD = f'openssl req -x509 -newkey rsa:4096 -keyout /etc/letsencrypt/key.pem \
        -out /etc/letsencrypt/cert.pem -days 365 -nodes -batch'

    thiscmd = OPENSSLCMD
    print('Running command ' + thiscmd)
    ans = os.popen(thiscmd).read()
    return 'New self-signed certificate created.'

@app.route("/letsencrypt")
def letsencrypt():
    """new_certificate
        ---
        parameters:
          - name: dry_run
            in: query
            required: false
          - name: test_cert
            in: query
            required: false
        """

    CERTBOTCMD = f'certbot certonly --standalone -n \
        -d {config["TLS_HOST"]} \
        -m {config["TLS_EMAIL"]} --agree-tos'

    dry_run = request.args.get('dry_run', default=False, type=bool)
    test_cert = request.args.get('test_cert', default=False, type=bool)
    thiscmd = CERTBOTCMD
    if dry_run:
        thiscmd = thiscmd + ' --dry-run'
    if test_cert:
        thiscmd = thiscmd + ' --test-cert'

    print('Running command ' + thiscmd)

    ans = os.popen(thiscmd).read()
    return ans

@app.route("/certificate_path")
def get_certificate_path():
    """certificate_path
            ---
            parameters: []
            """
    if config['TLS_TYPE'] == 'letsencrypt':
        ans = os.popen('certbot certificates').read()
        myexp = re.compile('Certificate Path: (.*)\n.*Private Key Path: (.*)\n')
        result = myexp.search(ans)
        if result:
            certs = {'cert': result.group(1),
                     'key': result.group(2)}
            return json.dumps(certs)
        else:
            return json.dumps({})

    if config['TLS_TYPE'] == 'self-signed':
        certfile = '/etc/letsencrypt/cert.pem'
        keyfile = '/etc/letsencrypt/key.pem'

        if os.path.isfile(certfile) and os.path.isfile(keyfile):
            certs = {'cert': certfile,
                     'key': keyfile}
            return json.dumps(certs)
        else:
            return json.dumps({})
    else:
        return json.dumps({})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

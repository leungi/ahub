import adal
import flask
from flask import Response
import uuid
import requests
import logging
import yaml

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

app = flask.Flask(__name__)
app.debug = False
app.secret_key = 'cdb94faf-f582-44c8-9413-812c3b67f3ff'


def read_config():
    """
    Read the ahub general config file
    """
    ans = {}
    with open("config.yaml", 'r') as stream:
        try:
            ans = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(format(exc))
    return ans


config = read_config()
debug = config['DEBUGMODE']

if debug:
    config['AAD_REDIRECT_HOST'] = 'localhost:8000'
    config['AAD_SCHEME'] = 'http'

AUTHORITY_URL = config['AAD_AUTHORITY_HOST_URL'] + '/' + config['AAD_TENANT']
REDIRECT_URI = f'{config["AAD_SCHEME"]}://{config["AAD_REDIRECT_HOST"]}/authorize'
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')


@app.route("/auth-proxy")
def main():
    if 'access_token' in flask.session:
        logging.info('Forwarding to location graphcall')
        return graphcall()
    else:
        logging.info('Forwarding to location login')
        return flask.Response(status=401)


@app.route("/login")
def login():
    flask.session['location'] = flask.request.headers.get('X-Target')
    logging.info('Gathered location {}'.format(flask.session['location']))
    auth_state = str(uuid.uuid4())
    flask.session['state'] = auth_state
    authorization_url = TEMPLATE_AUTHZ_URL.format(
        config['AAD_TENANT'],
        config['AAD_CLIENT_ID'],
        REDIRECT_URI,
        auth_state,
        config['AAD_RESOURCE'])
    resp = Response(status=200)
    resp.headers['Location'] = authorization_url
    return f'<script>window.location.replace("{authorization_url}")</script>'

    # f'<a href="{authorization_url}">Click to login to Microsoft.</a>'


@app.route("/authorize")
def getatoken():
    code = flask.request.args['code']
    state = flask.request.args['state']
    if state != flask.session['state']:
        raise ValueError("State does not match")
    auth_context = adal.AuthenticationContext(AUTHORITY_URL)
    token_response = auth_context.acquire_token_with_authorization_code(code, REDIRECT_URI, config['AAD_RESOURCE'],
                                                                        config['AAD_CLIENT_ID'],
                                                                        config['AAD_CLIENT_SECRET'])
    # It is recommended to save this to a database when using a production app.
    flask.session['access_token'] = token_response['accessToken']

    resp = Response(status=307)
    resp.headers['Location'] = flask.session['location']
    return resp


def graphcall():
    if 'access_token' not in flask.session:
        return flask.Response(status=401)
    endpoint = config['AAD_RESOURCE'] + '/' + config['AAD_API_VERSION'] + '/me/memberof'
    endpoint2 = config['AAD_RESOURCE'] + '/' + config['AAD_API_VERSION'] + '/me'
    http_headers = {'Authorization': 'Bearer ' + flask.session.get('access_token'),
                    'User-Agent': 'adal-python-sample',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'client-request-id': str(uuid.uuid4())}
    group_data = requests.get(endpoint, headers=http_headers, stream=False).json()
    me_data = requests.get(endpoint2, headers=http_headers, stream=False).json()

    if 'error' in group_data:
        return login()

    if config['AAD_AUTH_GROUP'] in [k['displayName'] for k in group_data['value']]:
        template = 'Login successful for user {0} in group {1}.'
        msg = template.format(me_data['displayName'], config['AAD_AUTH_GROUP'])
        logging.info(msg)
        return flask.Response(status=200)
    else:
        return flask.Response(status=401)


@app.route("/success")
def success():
    return "Login successful!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

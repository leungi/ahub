import json

import docker
from flasgger import Swagger
from flask import Flask, request, Response
from flask_cors import CORS

# local imports
from ahubdocker import *
from ahubredis import AhubRedis

# ----------------------------------------------------------
# REDIS AND DOCKER
# ----------------------------------------------------------

DEBUG = False

# set hostnames in case of local debugging
if DEBUG:
    config.REDISHOST = config.DEBUGHOST
    config.DOCKERHOST = 'localhost:2376'
    config.NGINXHOST = config.DEBUGHOST

# Init docker and redis objects
client = docker.DockerClient(base_url=config.DOCKERHOST)
ar = AhubRedis(config.REDISHOST)


# ----------------------------------------------------------
# FLASK
# ----------------------------------------------------------

# init Flask and set JSON as default response
class JSONResponse(Response):
    default_mimetype = 'application/json'


app = Flask(__name__)

CORS(app)  # activate CORS
app.response_class = JSONResponse
swagger = Swagger(app, config=config.SWAGGER)


# ----------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------


# DOCKER ENDPOINTS

@app.route("/get_services")
def get_services_api():
    """get_services
        ---
        parameters: []
        """
    return json.dumps(get_services(client))


@app.route("/update_nginx")
def update_nginx_api():
    """update_nginx
        ---
        parameters: []
        """
    return json.dumps(update_nginx(client))


# REDIS ENDPOINTS

@app.route("/get_redis_status")
def redis_status():
    """get_redis_status
        ---
        parameters: []
    """
    return json.dumps(ar.redis_status())


@app.route("/pid_log")
def pid_log_api():
    """pid_log
        ---
        parameters:
          - name: pid
            in: query
            required: true
          - name: msg
            in: query
            required: true
          - name: level
            in: query
            required: false
        """
    pid = request.args.get('pid')
    msg = request.args.get('msg')
    level = request.args.get('level')
    if not level:
        level = 'INFO'
    elif level not in {'INFO', 'WARNING', 'ERROR', 'DEBUG'}:
        return json.dumps({'error': 'please provide valid level - oneof (INFO, WARNING, ERROR, DEBUG)'})
    if not pid:
        return json.dumps({'error': 'please provide pid'})
    if not msg:
        return json.dumps({'error': 'please provide message'})

    return json.dumps({'logged': ar.pid_log(pid, msg, level)})


@app.route("/get_pid")
def get_pid_api():
    """get_pid
        ---
        parameters:
            - name: process_name
              in: query
              required: true
        """
    process_name = request.args.get('process_name')
    if not process_name:
        return json.dumps({'error': 'please provide process name'})
    else:
        return json.dumps({'pid': ar.get_pid(process_name)})


@app.route("/create_pid")
def create_pid_api():
    """create_pid
        ---
        parameters:
          - name: process_name
            in: query
            required: true
        """
    process_name = request.args.get('process_name')
    if not process_name:
        return json.dumps({'error': 'please provide process name'})
    else:
        return json.dumps({'pid': ar.create_pid(process_name)})


@app.route("/get_pid_info")
def get_pid_info_api():
    """get_pid_info
        ---
        parameters:
          - name: pid
            in: query
            required: true
        """
    pid = request.args.get('pid')
    if not pid:
        return json.dumps({'error': 'please provide pid'})
    else:
        return json.dumps(ar.get_pid_info(pid))


@app.route("/set_pid_status")
def set_pid_status_api():
    """set_pid_status
        ---
        parameters:
          - name: pid
            in: query
            required: true
          - name: status
            in: query
            required : true
        """
    pid = request.args.get('pid')
    status = request.args.get('status')
    if not pid:
        return json.dumps({'error': 'please provide pid'})
    if not status:
        return json.dumps({'error': 'please provide status'})
    else:
        return json.dumps({'status': ar.set_pid_status(pid, status)})


@app.route("/get_pid_log")
def get_pid_log_api():
    """get_pid_log
        ---
        parameters:
          - name: pid
            in: query
            required: true
        """
    pid = request.args.get('pid')
    if not pid:
        return json.dumps({'error': 'please provide pid'})
    else:
        return json.dumps(ar.get_pid_log(pid))


@app.route("/cleanup_pids")
def cleanup_pids_api():
    """cleanup_pids
        ---
        parameters: []
        """
    return json.dumps(ar.cleanup_pids())


@app.route("/get_all_pids")
def get_all_pids_api():
    """get_all_pids
        ---
        parameters: []
        """
    return json.dumps(ar.get_all_pids())


@app.route("/get_all_logs")
def get_all_logs_api():
    """get_all_logs
        ---
        parameters: []
        """
    return ar.get_all_logs().to_json(orient='records')


@app.route("/flushdb")
def redisflush():
    return json.dumps(ar.flush_db())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.BOSSPORT)

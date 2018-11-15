import pandas as pd
from flask import Flask, request, Response
from flasgger import Swagger
from redis import Redis, RedisError
from itertools import compress
import requests
import docker
import datetime
import re
import json
import logging
from nginxconfig import create_config

debug = False

# init Flask and set JSON as default response
class JSONResponse(Response):
    default_mimetype = 'application/json'

app = Flask(__name__)
app.response_class = JSONResponse

# Configure Swagger
SWAGGER_CONFIG = {
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

swagger = Swagger(app, config=SWAGGER_CONFIG)
bossport = 8000


# set hostnames
if(debug):
    redishost = 'ahub.westeurope.cloudapp.azure.com'
    dockerhost = 'localhost:2376'
    nginxhost = 'ahub.westeurope.cloudapp.azure.com'
else:
    redishost = "redis"
    dockerhost = 'unix://var/run/docker.sock'
    nginxhost = 'nginx'

# Connect to Redis
redis = Redis(host=redishost, db=0, socket_connect_timeout=2, socket_timeout=2)

# Connect to docker
client = docker.DockerClient(base_url=dockerhost)



def get_current_time():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")[:-3]


# %%

class RedisHandler(logging.Handler):
    def __init__(self, pid, level=0):
        super().__init__(level)
        self.pid = pid

    def emit(self, record):
        record.__dict__['pid'] = self.pid  # add the pid to the dict
        redis.lpush('log:' + self.pid, self.format(record))


class RedisLogger(object):
    def __init__(self, name, pid):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.handlers = []
        handler = RedisHandler(pid)
        formatter = logging.Formatter(fmt='%(levelname)s [%(asctime)s] PID %(pid)s: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        self._logger = logger

    def get(self):
        return self._logger


# pid = '1501'
# log = RedisLogger(pid).get()
# log.info('lol')

# %%

# %%

@app.route("/get_redis_status")
def redis_status():
    """get_redis_status
        ---
        parameters: []
        """
    try:
        redis.incr("counter")
        return json.dumps({'online': True})
    except RedisError:
        return json.dumps({'online': False})

def get_services():
    """Gives all active services on the docker swarm host and the nodes which have swagger compliant apis"""
    try:
        raw = [service.name for service in client.services.list()]
        services = [re.split(r'_', s)[1] for s in raw]
        swagger_resp = []
        for s in services:
            try:
                r = requests.get('http://{0}:8000/{1}/swagger.json'.format(nginxhost, s), timeout=.1)
            except Exception as err:
                swagger_resp.append(False)
            else:
                if r.status_code == 200:
                    swagger_resp.append(True)
                else:
                    swagger_resp.append(False)
        apis = list(compress(services, swagger_resp))

        try:
            apis.remove('boss')
        except ValueError:
            pass

    except Exception as err:
        return {'error': format(err)}
    else:
        return {'services': services,
                'apis': apis}

@app.route("/get_services")
def get_services_api():
    """get_services
        ---
        parameters: []
        """
    return json.dumps(get_services())

# CURRENTLY NOT WORKING
# config data cannot be updated on a live service
# breakdown and restart of nginx would be too much work right now
def update_nginx_config():
    nodes = get_services()['apis']
    new_conf = create_config(nodes)

    ind = [s.name for s in client.services.list()].index('ahub_nginx')
    nginx = client.services.list()[ind]
    client.configs.create(name= 'ahub_nginx.conf', data= new_conf)
    oldconf = client.configs.get('ahub_nginx.conf')

    client.services.create()


def pid_log(pid, msg, level='INFO'):
    log = RedisLogger('redislog', pid).get()
    print('writing message {0}'.format(msg))
    log.info(msg)
    return 'PID {0}: {1}'.format(pid, msg)


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

    return json.dumps({'logged': pid_log(pid, msg, level)})


# %%

# gets the latest pid for a process or create a new one if never run before
def get_pid(process_name):
    pid = redis.zrange(process_name, -1, -1)
    if not pid:
        pid = create_pid(process_name)
        return pid
    else:
        return pid[0].decode('utf-8')


# get_pid('batch')
# get_pid('bdusjhd')

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
        return json.dumps({'pid': get_pid(process_name)})


# get_pid_api('lol')

# %%
def decode_dict(d):
    ans = {}
    for k in d.keys():
        ans[k.decode('utf-8')] = d.get(k).decode('utf-8')
    return ans


def decode_list(l):
    return [k.decode('utf-8') for k in l]


def decode_set(s):
    return {k.decode('utf-8') for k in s}


# %%

# this function creates a new pid for a given process_name and sets the status to 'init'
def create_pid(process_name):
    redis.setnx('next_pid', 1000)
    redis.sadd('process_names', process_name)
    tstamp = float(get_current_time())
    pid = str(redis.incr('next_pid'))
    # add pid to sorted set [process_name], score is time
    redis.zadd(process_name, pid, tstamp)
    # create hash
    redis.hmset('process:' + pid,
                {'name': process_name,
                 'time': tstamp,
                 'status': 'init'})
    return pid


# create_pid('lolnais')

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
        return json.dumps({'pid': create_pid(process_name)})


# %%

# get all infos from a pid, current fields are
# name, time, status
def get_pid_info(pid):
    ans = redis.hgetall('process:' + str(pid))
    return (decode_dict(ans))


# get_pid_info('1510')

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
        return json.dumps(get_pid_info(pid))


# %%

def set_pid_status(pid, status):
    redis.hset('process:' + str(pid), 'status', status)
    return status


# set_pid_status('1510', 'aborted')

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
        return json.dumps({'status': set_pid_status(pid, status)})


# %%

# return all logs from a given pid
def get_pid_log(pid):
    ans = redis.lrange('log:' + str(pid), 0, -1)
    return decode_list(ans)


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
        return json.dumps(get_pid_log(pid))


# get_pid_log(1001)

# %%

# set all running pids to aborted
def cleanup_pids():
    allnames = decode_set(redis.smembers('process_names'))
    n = 0
    for process_name in allnames:
        pid = get_pid(process_name)
        if get_pid_info(pid)['status'] in ['running', 'init']:
            n += 1
            set_pid_status(pid, 'aborted')
            msg = 'Process aborted by cleanup process.'
            redis.hset('process:' + str(pid), 'error', msg)
    return n


@app.route("/cleanup_pids")
def cleanup_pids_api():
    """cleanup_pids
        ---
        parameters: []
        """
    return json.dumps(cleanup_pids())


# %%

# retrieve all pid's for all process_names
def get_all_pids():
    allnames = decode_set(redis.smembers('process_names'))
    ans = {}
    for process_name in allnames:
        ans[process_name] = decode_list(redis.zrange(process_name, 0, -1))
    return ans


@app.route("/get_all_pids")
def get_all_pids_api():
    """get_all_pids
        ---
        parameters: []
        """
    return json.dumps(get_all_pids())


# %%

# retrieve all logs
def get_all_logs():
    piddict = get_all_pids()
    logslist = []
    for process_name in piddict.keys():
        for pid in piddict[process_name]:
            log = get_pid_log(pid)
            logslist.append(pd.DataFrame({'log': log, 'pid': pid, 'logitem': list(range(len(log))), 'process_name': process_name}))

    ans = pd.concat(logslist)
    seq = ['process_name', 'pid', 'logitem', 'log']
    ans = ans.reindex(columns=seq)
    return ans


@app.route("/get_all_logs")
def get_all_logs_api():
    """get_all_logs
        ---
        parameters: []
        """
    return get_all_logs().to_json(orient='records')

# %%

@app.route("/")
def hello():
    try:
        redis.incr("counter")
        return json.dumps({'status': 'redis online'})
    except RedisError:
        return json.dumps({'error': 'cannot connect to redis'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=bossport)

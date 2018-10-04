from flask import Flask, request
from redis import Redis, RedisError
import datetime
import pandas as pd
import json
import logging

app = Flask(__name__)
bossport = 8003

# Connect to Redis
redishost = "localhost"
redis = Redis(host=redishost, db=0, socket_connect_timeout=2, socket_timeout=2)


# %%

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

def pid_log(pid, msg, level='INFO'):
    log = RedisLogger('redislog', pid).get()
    print('writing message {0}'.format(msg))
    log.info(msg)
    return 'PID {0}: {1}'.format(pid, msg)


@app.route("/pid_log")
def pid_log_api():
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


# cleanup_pids()

# %%

# retrieve all pid's for all process_names
def get_all_pids():
    allnames = decode_set(redis.smembers('process_names'))
    ans = {}
    for process_name in allnames:
        ans[process_name] = decode_list(redis.zrange(process_name, 0, -1))
    return ans


# get_all_pids()
# %%

# retrieve all logs
def get_all_logs():
    piddict = get_all_pids()
    logslist = []
    for process_name in piddict.keys():
        for pid in piddict[process_name]:
            log = get_pid_log(pid)
            logslist.append(pd.DataFrame({'log': log, 'pid': pid, 'process_name': process_name}))

    ans = pd.concat(logslist)
    seq = ['process_name', 'pid', 'log']
    ans = ans.reindex(columns=seq)
    return ans


# get_all_logs()


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

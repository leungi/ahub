import logging
import pandas as pd
import datetime
import yaml
from redis import Redis, RedisError


class RedisHandler(logging.Handler):
    def __init__(self, pid, rediscon, level=0):
        super().__init__(level)
        self.pid = pid
        self.rediscon = rediscon

    def emit(self, record):
        record.__dict__['pid'] = self.pid  # add the pid to the dict
        self.rediscon.lpush('log:' + self.pid, self.format(record))


class RedisLogger(object):
    def __init__(self, name, pid, rediscon):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.handlers = []
        handler = RedisHandler(pid, rediscon)
        formatter = logging.Formatter(fmt='%(levelname)s [%(asctime)s] PID %(pid)s: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        self._logger = logger

    def get(self):
        return self._logger


def get_current_time():
    return datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S.%f")[:-3]


class AhubRedis:
    def __init__(self):

        self.config = {}
        self.read_config()
        self.debug = self.config['DEBUGMODE']
        if self.debug:
            self.redishost = self.config['DEBUGHOST']
        else:
            self.redishost = 'redis'
        self.rediscon = Redis(host=self.redishost, db=0, socket_connect_timeout=2, socket_timeout=2)

        if self.redis_status()['online']:
            print('Redis connection established.')
        else:
            print('Redis connection failed.')

    def read_config(self):
        """Read the ahub general config file"""
        with open("config.yaml", 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(format(exc))

    # log a message to redis for given pid
    def pid_log(self, pid, msg, level='INFO'):
        log = RedisLogger('redislog', pid, self.rediscon).get()
        print('writing message {0}'.format(msg))
        if level == 'DEBUG':
            log.debug(msg)
        elif level == 'WARNING':
            log.warning(msg)
        elif level == 'ERROR':
            log.error(msg)
        else:
            log.info(msg)
        return 'PID {0}: {1}'.format(pid, msg)

    def redis_status(self):
        try:
            self.rediscon.incr("counter")
            return {'online': True}
        except RedisError:
            return {'online': False}

    # gets the latest pid for a process or create a new one if never run before
    def get_pid(self, process_name):
        pid = self.rediscon.zrange(process_name, -1, -1)
        if not pid:
            pid = self.create_pid(process_name)
            return pid
        else:
            return pid[0].decode('utf-8')

    @staticmethod
    def decode_dict(d):
        ans = {}
        for k in d.keys():
            ans[k.decode('utf-8')] = d.get(k).decode('utf-8')
        return ans

    @staticmethod
    def decode_list(l):
        return [k.decode('utf-8') for k in l]

    @staticmethod
    def decode_set(s):
        return {k.decode('utf-8') for k in s}

    # this function creates a new pid for a given process_name and sets the status to 'init'
    def create_pid(self, process_name):
        self.rediscon.setnx('next_pid', 1000)
        self.rediscon.sadd('process_names', process_name)
        tstamp = float(get_current_time())
        pid = str(self.rediscon.incr('next_pid'))
        # add pid to sorted set [process_name], score is time
        self.rediscon.zadd(process_name, {pid: tstamp})
        # create hash
        self.rediscon.hmset('process:' + pid,
                            dict(name=process_name, time=tstamp, status='init'))
        return pid

    # get all infos from a pid, current fields are
    # name, time, status
    def get_pid_info(self, pid):
        ans = self.rediscon.hgetall('process:' + str(pid))
        return self.decode_dict(ans)

    # set the status for a given pid
    def set_pid_status(self, pid, status):
        self.rediscon.hset('process:' + str(pid), 'status', status)
        return status

    # return all logs from a given pid
    def get_pid_log(self, pid):
        ans = self.rediscon.lrange('log:' + str(pid), 0, -1)
        return self.decode_list(ans)

    # set all running pids to aborted
    def cleanup_pids(self):
        allnames = self.decode_set(self.rediscon.smembers('process_names'))
        n = 0
        for process_name in allnames:
            pid = self.get_pid(process_name)
            if self.get_pid_info(pid)['status'] in ['running', 'init']:
                n += 1
                self.set_pid_status(pid, 'aborted')
                msg = 'Process aborted by cleanup process.'
                self.rediscon.hset('process:' + str(pid), 'error', msg)
        return n

    # retrieve all pid's for all process_names
    def get_all_pids(self):
        allnames = self.decode_set(self.rediscon.smembers('process_names'))
        ans = {}
        for process_name in allnames:
            ans[process_name] = self.decode_list(self.rediscon.zrange(process_name, 0, -1))
        return ans

    # retrieve all logs
    def get_all_logs(self):
        piddict = self.get_all_pids()
        logslist = []
        for process_name in piddict.keys():
            for pid in piddict[process_name]:
                log = self.get_pid_log(pid)
                logslist.append(pd.DataFrame(
                    {'log': log, 'pid': pid, 'logitem': list(range(len(log))), 'process_name': process_name}))

        ans = pd.concat(logslist)
        seq = ['process_name', 'pid', 'logitem', 'log']
        ans = ans.reindex(columns=seq)
        return ans

    def flush_db(self):
        try:
            self.rediscon.flushdb()
            return {'status': 'redis db flushed'}
        except RedisError:
            return {'error': 'cannot connect to redis'}

import threading
import json
from datetime import datetime
import time
from bossclient import Boss

myboss = Boss('localhost', 8002)


# DEBUG
# myboss.get_pid('batch')
# pid = myboss.create_pid('batch')
# myboss.log(pid, 'test du bauer')
# myboss.get_pid_info(pid)
# %%


def batch(force=0, t=20):
    process_name = 'batch'
    pid = myboss.get_pid(process_name)
    pid_info = myboss.get_pid_info(pid)

    # has the process already finished today
    run_today = (datetime.strptime(pid_info['time'][0:8], '%Y%m%d').date() ==
                 datetime.today().date()) & (pid_info['status'] == 'finished')

    # check if process has not run today and is not finished and force is FALSE
    if (not run_today) | force:
        # if yes, check if process is not running
        if pid_info['status'] != 'running':
            if pid_info['status'] != 'init':
                pid = myboss.create_pid(process_name)
            kwargs = {'pid': pid, 'process_name': process_name, 't': t}
            # custom args
            threading.Thread(target=batch_proc, kwargs=kwargs)

            return json.dumps({'msg': 'Process {0} started...'.format(process_name),
                               'log': myboss.get_pid_log(pid),
                               'status': 'started'})

        else:
            return json.dumps({'msg': 'Process {0} currently running...'.format(process_name),
                               'log': myboss.get_pid_log(pid),
                               'status': 'running'})
    else:
        return json.dumps({'msg': 'Process {0} finished.'.format(process_name),
                           'log': myboss.get_pid_log(pid),
                           'status': 'finished'})


def batch_proc(**kwargs):
    pid = kwargs['pid']
    process_name = kwargs['process_name']
    myboss.log(pid, 'Process {0} has started...'.format(process_name))
    myboss.set_pid_status(kwargs['pid'], 'running')

    # do some stuff #############
    time.sleep(kwargs['t'])
    ##################################

    # wrap up
    myboss.log(pid, 'Process {0} finished'.format(process_name))
    myboss.set_pid_status(pid, 'finished')

    return True


# debug

batch_proc(pid ='1001', process_name='batch', t=1)

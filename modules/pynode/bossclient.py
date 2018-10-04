import requests
import json


class Boss:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @staticmethod
    def _throw_error(ans):
        msg = {'error': 'status {0}, reason {1}'.format(ans.status_code, ans.reason)}
        print(msg)
        return msg

    def get_pid(self, process_name):
        ans = requests.get('http://{0}:{1}/get_pid'.format(self.host, self.port), {'process_name': process_name})
        if ans.status_code == 200:
            return json.loads(ans.content.decode('utf-8'))['pid']
        else:
            return self._throw_error(ans)

    def create_pid(self, process_name):
        ans = requests.get('http://{0}:{1}/create_pid'.format(self.host, self.port), {'process_name': process_name})
        if ans.status_code == 200:
            return json.loads(ans.content.decode('utf-8'))['pid']
        else:
            return self._throw_error(ans)

    def get_pid_info(self, pid):
        ans = requests.get('http://{0}:{1}/get_pid_info'.format(self.host, self.port), {'pid': pid})
        if ans.status_code == 200:
            return json.loads(ans.content.decode('utf-8'))
        else:
            return self._throw_error(ans)

    def set_pid_status(self, pid, status):
        ans = requests.get('http://{0}:{1}/set_pid_status'.format(self.host, self.port), {'pid': pid, 'status': status})
        if ans.status_code == 200:
            return json.loads(ans.content.decode('utf-8'))
        else:
            return self._throw_error(ans)

    def get_pid_log(self, pid):
        ans = requests.get('http://{0}:{1}/get_pid_log'.format(self.host, self.port), {'pid': pid})
        if ans.status_code == 200:
            return json.loads(ans.content.decode('utf-8'))
        else:
            return self._throw_error(ans)

    def log(self, pid, msg):
        ans = requests.get('http://{0}:{1}/pid_log'.format(self.host, self.port), {'pid': pid, 'msg': msg})
        if ans.status_code == 200:
            return json.loads(ans.content.decode('utf-8'))
        else:
            return self._throw_error(ans)


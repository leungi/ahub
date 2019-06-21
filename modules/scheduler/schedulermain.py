import requests
import json
import yaml


class Scheduler:
    def __init__(self):
        self.config = {}
        self.read_config()
        if self.config['DEBUGMODE']:
            self.nginxhost = self.config['DEBUGHOST']
        else:
            self.nginxhost = 'nginx'

    def read_config(self):
        """
        Read the ahub general config file
        """
        with open("config.yaml", 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(format(exc))

    def check_apis(self, apis):
        print('Checking for new API...')
        found = False
        try:
            ans = requests.get('http://{0}:{1}/boss/get_services'.format(self.nginxhost, 8000))
        except requests.RequestException:
            print('Could not establish connection to boss.')
            return apis

        raw = json.loads(ans.content)
        newapis = list(set(raw['apis']).union(raw['html']))
        for a in newapis:
            if a not in apis:
                found = True
                print('New api found: {0}'.format(a))
        if found:
            print('Updating nginx config.')
            try:
                requests.get('http://{0}:{1}/boss/reload'.format(self.nginxhost, 8000))
            except requests.RequestException:
                print('Could not update nginx config.')
                return apis
        else:
            print('Nothing new.')
        return newapis

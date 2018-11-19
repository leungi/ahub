import requests
import json
import config
import logging


class Checker:
    def __init__(self):
        log = logging.getLogger('checker')
        log.setLevel(logging.DEBUG)
        #handler = logging.Handler(logging.DEBUG)
        #handler.setFormatter(logging.Formatter(fmt='%(levelname)s [%(asctime)s]: %(message)s',
        #                                       datefmt='%Y-%m-%d %H:%M:%S'))
        #log.addHandler(handler)
        self.log = log

    def check_apis(self, apis):
        self.log.error('Checking for new API...')
        found = False
        try:
            ans = requests.get('http://{0}:{1}/boss/get_services'.format(config.NGINXHOST, config.BOSSPORT))
        except requests.RequestException:
            self.log.error('Could not establish connection to boss.')
            return apis

        newapis = json.loads(ans.content)['apis']
        for a in newapis:
            if a not in apis:
                found = True
                self.log.info('New api found: {0}'.format(a))
        if found:
            self.log.info('Updating nginx config.')
            try:
                requests.get('http://{0}:{1}/boss/update_nginx'.format(config.NGINXHOST, config.BOSSPORT))
            except requests.RequestException:
                logging.error('Could not update nginx config.')
                return apis
        return newapis

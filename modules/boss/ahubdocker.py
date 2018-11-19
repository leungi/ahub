from itertools import compress
import requests
from docker.types.services import ConfigReference
import re
from nginxconfig import create_config
from ahubredis import get_current_time
import config


def get_services(client, debug=False):
    """Gives all active services on the docker swarm host and the nodes which have swagger compliant apis"""
    try:
        raw = [service.name for service in client.services.list()]
        services = [re.split(r'_', s)[1] for s in raw]

        potential_apis = [s for s in services if s not in config.AHUBSTACK]
        swagger_resp = []
        html_resp = []
        for s in potential_apis:
            try:
                if debug:
                    r = requests.get('http://{0}:8000/{1}/swagger.json'.format(config.NGINXHOST, s), timeout=.5)
                else:
                    r = requests.get('http://{0}:8000/swagger.json'.format(s), timeout=.5)
            except requests.RequestException:
                swagger_resp.append(False)
            else:
                if r.status_code == 200:
                    swagger_resp.append(True)
                else:
                    swagger_resp.append(False)

            try:
                if debug:
                    r = requests.get('http://{0}:8000/{1}/'.format(config.NGINXHOST, s))
                else:
                    r = requests.get('http://{0}:8000/'.format(s), timeout=5)
            except requests.RequestException:
                html_resp.append(False)
            else:
                if r.status_code == 200:
                    html_resp.append(True)
                else:
                    html_resp.append(False)

        html = list(compress(potential_apis, html_resp))
        apis = list(compress(potential_apis, swagger_resp))
        apis.sort()
        services.sort()
        html.sort()

    except Exception as err:
        return {'error': format(err)}
    else:
        return {'services': services,
                'apis': apis,
                'html': html}


def update_nginx(client, debug=False):
    nginx = client.services.get([s.name for s in client.services.list() if "nginx" in s.name][0])
    # oldconf = client.configs.get([c.name for c in client.configs.list() if 'nginx' in c.name][0])

    # create new config
    if debug:
        nodes = ['node1', 'node2']
    else:
        nodes = get_services(client, debug)['apis']

    newconfdata = create_config(nodes)
    print(newconfdata["config"])
    confname = 'ahub_nginx_' + get_current_time() + '.conf'
    try:
        client.configs.create(name=confname, data=newconfdata["config"])
    except KeyError:
        pass

    # get new config and create ref
    newconf = client.configs.get(confname)

    newref = ConfigReference(newconf.id, newconf.name, '/etc/nginx/nginx.conf')

    # update nginx
    nginx.update(configs=[newref])

    # remove old nginx configs
    p = re.compile('.+nginx_\d+.\d+\.conf') # pattern for configs with timestamp
    for oldconf in [s for s in client.configs.list() if p.match(s.name)]:
        if oldconf.name != confname:
            oldconf.remove()

    return {"newconfig": confname}

import docker
import time
import json
import docker.types
import re
import datetime
import requests
from base64 import urlsafe_b64encode
import yaml
from itertools import compress


def get_current_time():
    return datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S.%f")[:-3]


class Ahub(object):
    """
    This is the class that cares for the overall control of the ahub framework.
    Its main function is to ramp up the service stack with the appropriate configuration.
    - nginx reverse proxy
    - certbot for TSL certificate handling
    - portainer GUI for easy stack management
    - gui for easy testing of API endpoints
    - redis as a process repository
    """

    def __init__(self):
        self.debug = False
        self.dockerhost = 'unix://var/run/docker.sock'
        self.nginxhost = 'nginx'
        self.network_name = ''
        self.stack_name = ''
        self.dockerclient = None
        self.config = {}
        self.cert = {}
        self.volumes = []
        self.stack = ['boss']
        self.tlsactive = False
        self.health = {}
        self.reload()

    def reload(self):
        self.health['config'] = self.read_config()  # read the config from yaml file
        self.debug = self.config['DEBUGMODE']
        if self.debug:
            self.dockerhost = 'localhost:2376'
            self.nginxhost = self.config['DEBUGHOST']
        try:
            self.dockerclient = docker.DockerClient(base_url=self.dockerhost)
            self.dockerclient.version()
        except Exception as err:
            print(err)
            print('Connection to docker host at ' + self.dockerhost + ' can not be established.')
            return False
        self.health['network'] = self.get_network_name()
        self.health['stack'] = self.get_stack_name()
        self.health['volumes'] = self.create_volumes()  # create necessary mount volumes
        self.health['portainer'] = self.start_service('portainer')
        self.health['redis'] = self.start_service('redis')
        self.health['nginx'] = self.start_service('nginx')
        self.health['certbot'] = self.start_service('certbot')
        self.health['scheduler'] = self.start_service('scheduler')
        self.health['gui'] = self.start_service('gui')
        if self.config['AUTH_TYPE'] == 'aad':
            self.health['aadauth'] = self.start_service('aadauth')
        self.update_nginx()  # update nginx configuration
        if self.check_certificate() and not self.tlsactive:
            print('Reloading nginx to apply certificate.')
            self.update_nginx()
        self.health['tls'] = self.tlsactive

        return True

    def validate_config(self):
        print('Validating config...')
        flag = True
        if self.config['VERSION'] in ['2.0']:
            print('Please select valid VERSION (currently only 2.0)')
            flag = False

        if self.config['TLS_TYPE'] not in ['letsencrypt', 'self-signed']:
            print('Please choose valid TLS_TYPE (letsencrypt or self-signed)')
            flag = False

        if self.config['TLS_TYPE'] == 'letsencrypt':
            necessary = ['TLS_HOST', 'TLS_EMAIL']
            for k in necessary:
                if k not in self.config.keys():
                    print('You have chosen TLS_TYPE letsencrypt. Please provide mandatory config field: ' + k)
                    flag = False

        if self.config['AUTH_TYPE'] not in ['none', 'basic', 'aad']:
            print('Please choose valid AUTH_TYPE (none, basic or aad')
            flag = False

        if self.config['AUTH_TYPE'] == 'aad':
            necessary = ['AAD_RESOURCE', 'AAD_TENANT', 'AAD_AUTHORITY_HOST_URL', 'AAD_CLIENT_ID',
                         'AAD_CLIENT_SECRET', 'AAD_REDIRECT_HOST', 'AAD_SCHEME', 'AAD_AUTH_GROUP',
                         'AAD_API_VERSION']
            for k in necessary:
                if k not in self.config.keys():
                    print('You have chosen AUTH_TYPE aad. Please provide mandatory config field: ' + k)
                    flag = False

        if self.config['OPEN_8000']:
            print('WARNING: Port 8000 is open for all services. Only for debugging purposes.')

        if self.config['OPEN_9000']:
            print('WARNING: Port 9000 is open on portainer. Only for debugging purposes.')

        if self.config['OPEN_6379']:
            print('WARNING: Port 6379 is open on redis. Only for debugging purposes.')

        if not flag:
            print('Config errors have been found. AHUB launch has been aborted.')

        return flag

    def get_network_name(self):
        boss_name = [s.name for s in self.dockerclient.services.list() if 'boss' in s.name]
        if boss_name:
            boss = self.dockerclient.services.get(boss_name[0])
            network_id = boss.attrs['Endpoint']['VirtualIPs'][0]['NetworkID']
            self.network_name = self.dockerclient.networks.get(network_id).name
            print('Network name is ' + self.network_name)
            return True
        else:
            print('Virtual network name could not be identified.')
            return False

    def get_stack_name(self):
        boss_name = [s.name for s in self.dockerclient.services.list() if 'boss' in s.name]
        if boss_name:
            boss = self.dockerclient.services.get(boss_name[0])
            self.stack_name = boss.attrs['Spec']['Labels']['com.docker.stack.namespace']
            print('Stack name is ' + self.stack_name)
            return True
        else:
            print('Stack name could not be identified.')
            return False


    def get_nginx_status(self):
        """
        Polls the status of the nginx service
        :return: True if status is 'running
        """
        nginx = [s for s in self.dockerclient.services.list() if 'nginx' in s.name]
        if nginx:
            nginx[0].reload()
            states = [t['Status']['State'] for t in nginx[0].tasks()]
            if 'running' in states:
                return True
        return False

    def report_health(self):
        return self.health

    def get_config_reference(self):
        """
        Gets the config reference object for the overall ahub config file, which
        should be available in the stack (must be configured in the compose file to run ahub)
        :return: ConfigReference object
        """
        cref = [s for s in self.dockerclient.configs.list() if 'main_config' in s.name]
        if cref:
            newref = docker.types.ConfigReference(cref[0].id, cref[0].name, '/app/config.yaml')
            return newref
        else:
            print('Could not find ahub config in stack.')
            return None

    def get_secret_reference(self):
        """
        Gets the secret reference object for the http basic authentication, which
        should be available in the stack (must be configured in the compose file to run ahub)
        :return: SecretReference object
        """
        sref = [s for s in self.dockerclient.secrets.list() if 'htpasswd' in s.name]
        if sref:
            newref = docker.types.SecretReference(sref[0].id, sref[0].name, filename='.htpasswd')
            return newref
        else:
            print('Could not find secret htpasswd in stack.')
            return None

    def read_config(self):
        """
        Read the ahub general config file
        """
        with open("config.yaml", 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print('Config file could not be read.')
                print(format(exc))

        return self.validate_config()


    def check_docker(self):
        """
        Check if the docker socket is available
        :return: True when docker socket is connected
        """
        try:
            self.dockerclient.version()
        except Exception as err:
            print(format(err))
            return False
        else:
            return True

    def check_certificate(self):
        """
        Polls the API endpoints of certbot to get the path to the certificate file and key
        :return: bool True if certificates are available
        """
        print('Polling certbot...', end='')
        ct = 0
        retry_success = False
        ans = None
        while ct <= 5 and not retry_success:
            try:
                ans = requests.get('http://{0}:{1}/certbot/certificate_path'.format(self.nginxhost, '8000'))
            except requests.RequestException:
                ct = ct + 1
                print('.', end='')
                time.sleep(0.2)
            else:
                retry_success = True

        if not retry_success:
            print('Could not establish connection to certbot.')
            return False

        if ans.status_code == 200:
            ans_parsed = json.loads(ans.content)
            if ans_parsed:
                self.cert = ans_parsed
                print('Certificate is good.')
                return True
            else:
                print('Certificate not found. Applying for new one...')
                if self.apply_for_certificate():
                    return self.check_certificate()  # need to stop endless loop
                else:
                    print('Certificate could not be installed. Services will not be reachable under ports 80 and 443.')
                    return False
                    # TODO: automatic fallback to self-signed. For this to work, the global config
                    #       needs to be changed and uploaded to the stack
                    #if self.config['TLS_TYPE'] == 'letsencrypt':
                    #    print('Falling back to self-signed certificate.')
                    #    self.config['TLS_TYPE'] = 'self-signed'
                    #    return self.check_certificate()
                    #else:
                    #    return False
        else:
            print(ans.status_code)
            return False

    def apply_for_certificate(self):
        if self.config['TLS_TYPE'] == 'letsencrypt':
            endpoint = 'letsencrypt'
        else:
            endpoint = 'openssl'
        try:
            ans = requests.get('http://{0}:{1}/certbot/{2}'.format(self.nginxhost, '8000', endpoint))
        except requests.RequestException:
            print('Could not establish connection to certbot.')
            return False
        else:
            response = ans.content.decode("utf-8")
            print(response)
            if response:
                print('Certificate successfully created.')
                return True
            else:
                print('ERROR: {0} certificate could not be created. Please check certbot logs.'.format(self.config['TLS_TYPE']))
                return False

    def start_service(self, name):
        """
        Start a given service
        :return: bool
        """
        nginx_id = [s.id for s in self.dockerclient.services.list() if name in s.name]
        if nginx_id:
            print(name + ' already running.')
            if name not in self.stack:
                self.stack.append(name)
            return True
        try:
            creator = {
                'nginx': self.create_nginx,
                'certbot': self.create_certbot,
                'portainer': self.create_portainer,
                'redis': self.create_redis,
                'scheduler': self.create_scheduler,
                'aadauth': self.create_aadauth,
                'gui': self.create_gui
            }
            if name not in creator:
                print(name + 'is not a valid service')
                return False
            creator[name]()
        except Exception as err:
            print(name + ' startup failed.')
            print(format(err))
            return False
        else:
            if name not in self.stack:
                self.stack.append(name)
            print(name + ' successfully started.')
            return True

    def create_nginx(self):
        ports = {80: 80,
                 443: 443}
        if self.config['OPEN_8000']:
            ports[8000] = 8000

        sref = self.get_secret_reference()
        self.dockerclient.services.create(image='nginx',
                                          name='nginx',
                                          constraints=['node.role==manager'],
                                          networks=[self.network_name],
                                          endpoint_spec=docker.types.EndpointSpec(ports=ports),
                                          labels={'com.docker.stack.image': 'nginx',
                                                  'com.docker.stack.namespace': self.stack_name},
                                          container_labels={'com.docker.stack.namespace': self.stack_name},
                                          mounts=['tls:/etc/letsencrypt:ro'],
                                          secrets=[sref])

    def create_redis(self):
        ports = {}
        if self.config['OPEN_6379']:
            ports[6379] = 6379

        self.dockerclient.services.create(image='redis:alpine',
                                          name='redis',
                                          constraints=['node.role==manager'],
                                          networks=[self.network_name],
                                          endpoint_spec=docker.types.EndpointSpec(ports=ports),
                                          labels={'com.docker.stack.image': 'redis:alpine',
                                                  'com.docker.stack.namespace': self.stack_name},
                                          container_labels={'com.docker.stack.namespace': self.stack_name},
                                          mounts=['redis:/data:rw'])

    def create_certbot(self):
        cref = self.get_config_reference()
        self.dockerclient.services.create(image='qunis/ahub_certbot:{0}'.format(str(self.config['VERSION'])),
                                          name='certbot',
                                          constraints=['node.role==manager'],
                                          networks=[self.network_name],
                                          env=['PYTHONUNBUFFERED=1'],
                                          labels={'com.docker.stack.image': 'qunis/ahub_certbot',
                                                  'com.docker.stack.namespace': self.stack_name},
                                          container_labels={'com.docker.stack.namespace': self.stack_name},
                                          mounts=['tls:/etc/letsencrypt:rw'],
                                          configs=[cref])

    def create_portainer(self):
        ports = {}
        if self.config['OPEN_9000']:
            ports[9000] = 9000
        self.dockerclient.services.create(image='portainer/portainer',
                                          name='portainer',
                                          constraints=['node.role==manager'],
                                          networks=[self.network_name],
                                          endpoint_spec=docker.types.EndpointSpec(ports=ports),
                                          labels={'com.docker.stack.image': 'portainer/portainer',
                                                  'com.docker.stack.namespace': self.stack_name},
                                          container_labels={'com.docker.stack.namespace': self.stack_name},
                                          mounts=['portainer:/data:rw',
                                                  '/var/run/docker.sock:/var/run/docker.sock'])

    def create_scheduler(self):
        cref = self.get_config_reference()
        self.dockerclient.services.create(image='qunis/ahub_scheduler:{0}'.format(str(self.config['VERSION'])),
                                          name='scheduler',
                                          networks=[self.network_name],
                                          env=['PYTHONUNBUFFERED=1'],
                                          labels={'com.docker.stack.image': 'qunis/ahub_scheduler',
                                                  'com.docker.stack.namespace': self.stack_name},
                                          container_labels={'com.docker.stack.namespace': self.stack_name},
                                          configs=[cref])

    def create_aadauth(self):
        cref = self.get_config_reference()
        self.dockerclient.services.create(image='qunis/ahub_aadauth:{}'.format(str(self.config['VERSION'])),
                                          name='aadauth',
                                          networks=[self.network_name],
                                          env=['PYTHONUNBUFFERED=1'],
                                          labels={'com.docker.stack.image': 'qunis/ahub_aadauth',
                                                  'com.docker.stack.namespace': self.stack_name},
                                          container_labels={'com.docker.stack.namespace': self.stack_name},
                                          configs=[cref])

    def create_gui(self):
        cref = self.get_config_reference()
        self.dockerclient.services.create(image='qunis/ahub_reactgui:{}'.format(str(self.config['VERSION'])),
                                          name='gui',
                                          networks=[self.network_name],
                                          labels={'com.docker.stack.image': 'qunis/ahub_reactgui',
                                                  'com.docker.stack.namespace': self.stack_name},
                                          container_labels={'com.docker.stack.namespace': self.stack_name},
                                          configs=[cref])

    def create_volumes(self):
        """Create all necessary volumes"""
        try:
            self.volumes = []
            for v in ['tls', 'portainer', 'redis']:
                self.dockerclient.volumes.create(v)
                self.volumes.append(v)
        except Exception:
            print('Volume creation has failed.')
            return False
        else:
            return True

    def stop_service(self, name):
        """Stop a given service"""
        s_id = [s.id for s in self.dockerclient.services.list() if name in s.name]
        if s_id:
            try:
                self.dockerclient.services.get(s_id.pop()).remove()
            except Exception as err:
                print(format(err))
            else:
                if name in self.stack:
                    self.stack.remove(name)
                print(name + ' successfully removed.')
                return True
        else:
            print(name + ' not found.')
            return False

    def update_nginx(self):
        """
        Updates the nginx configuration.
        :return:
        """
        if 'nginx' not in self.stack:
            print('Nginx not running.')
            return False
        client = self.dockerclient
        nginx = client.services.get([s.name for s in client.services.list() if "nginx" in s.name][0])

        # create new config
        nodes = self.get_nodes()

        newconfdata = self.create_config(nodes)
        # print(newconfdata["config"])
        confname = 'ahub_nginx_' + get_current_time() + '.conf'
        try:
            client.configs.create(name=confname, data=newconfdata["config"])
        except KeyError:
            pass

        # get new config and create ref
        newconf = client.configs.get(confname)
        newref = docker.types.ConfigReference(newconf.id, newconf.name, '/etc/nginx/nginx.conf')

        # update nginx
        nginx.update(configs=[newref])

        # remove old nginx configs
        p = re.compile('.+nginx_\d+.\d+\.conf')  # pattern for configs with timestamp
        for oldconf in [s for s in client.configs.list() if p.match(s.name)]:
            if oldconf.name != confname:
                oldconf.remove()

        print('\tWaiting for nginx to ramp up again.', end='')
        while not self.get_nginx_status():
            print('.', end='')
            time.sleep(.5)
        print('Done!')

        return {"newconfig": confname}

    def get_nodes(self):
        """
        Polls the docker API for all nodes which are not yet mentioned in self.stack
        :return:
        """
        client = self.dockerclient
        raw = [service.name for service in client.services.list()]
        services = [re.sub(self.stack_name + '_', '', s) for s in raw]
        potential_apis = [s for s in services if s not in self.stack]
        return potential_apis

    def get_services(self):
        """Gives all active services on the docker swarm host and the nodes which have swagger compliant apis"""
        client = self.dockerclient

        try:
            raw = [service.name for service in client.services.list()]
            services = [re.sub(self.stack_name + '_', '', s) for s in raw]

            potential_apis = [s for s in services if s not in self.stack]
            swagger_response = []
            html_response = []
            for s in potential_apis:
                try:
                    r = requests.get('http://{0}:8000/{1}/swagger.json'.format(self.nginxhost, s),
                                     timeout=.5)

                except requests.RequestException:
                    swagger_response.append(False)
                else:
                    if r.status_code == 200:
                        swagger_response.append(True)
                    else:
                        swagger_response.append(False)

                try:
                    r = requests.get('http://{0}:8000/{1}/'.format(self.nginxhost, s))
                except requests.RequestException:
                    html_response.append(False)
                else:
                    if r.status_code == 200:
                        html_response.append(True)
                    else:
                        html_response.append(False)

            html = list(compress(potential_apis, html_response))
            apis = list(compress(potential_apis, swagger_response))
            apis.sort()
            services.sort()
            html.sort()

        except Exception as err:
            return {'error': format(err)}
        else:
            return {'services': services,
                    'apis': apis,
                    'html': html}

    def create_config(self, nodes):
        """
        Builds the nginx config file from templates
        :param nodes: list of str, nodenames which should be added as routing endpoints
        :return: dict[config, config_enc] the resulting config file both raw and encoded
        """
        config = open('templates/nginx_template.conf', mode='r').read()
        node_template = open('templates/node_template.conf', mode="r").read()
        server_template = open('templates/server_template.conf', mode="r").read()
        service_template = open('templates/service_template.conf', mode="r").read()
        auth_template_basic = open('templates/auth_template_basic.conf', mode="r").read()
        auth_template_aad = open('templates/auth_template_aad.conf', mode="r").read()

        tab = "    "
        print('Updating nginx config...')
        # add location part
        location = []
        for n in nodes:
            print('\tAdding node ' + n)
            # Location part
            insert = node_template.replace("#NODE", n)
            for s in [2 * tab + s for s in re.split("\n", insert)]:
                location.append(s)

        config = config.replace('#NODEBLOCK', "\n".join(location))
        config = config.replace('#SERVICEBLOCK', service_template)
        server_template = server_template.replace('#LOCATIONBLOCK', "\n".join(location))

        # add server block when tls certificate can be retrieved
        if self.cert:
            self.tlsactive = True
            print('\tAdding server block with encryption: ' + self.config['TLS_TYPE'])
            server_template = server_template.replace('#CERTIFICATE', self.cert['cert'])
            server_template = server_template.replace('#KEY', self.cert['key'])
            config = config.replace('#SERVERBLOCK', server_template)

        if self.config['AUTH_TYPE'] == 'none':
            print('CAUTION: No authentication')
            config = config.replace('#SERVICEBLOCK', service_template)
            config = config.replace('#NODEBLOCK', "\n".join(location))

        if self.config['AUTH_TYPE'] == 'basic':
            print('\tAdding authentication block: ' + self.config['AUTH_TYPE'])
            config = config.replace('#AUTHBLOCK', auth_template_basic)
            config = config.replace('#SERVICEBLOCK', service_template)
            config = config.replace('#NODEBLOCK', "\n".join(location))

        if self.config['AUTH_TYPE'] == 'aad':
            print('\tAdding authentication block: ' + self.config['AUTH_TYPE'])
            config = config.replace('#AUTHBLOCK', auth_template_aad)



        config_enc = urlsafe_b64encode(config.encode('utf-8'))

        with open('test.txt', 'w') as file:
            file.write(config)

        return {"config": config, "config_enc": config_enc}
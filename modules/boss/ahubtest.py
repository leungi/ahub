from ahubmain import Ahub

ahub = Ahub()
self = ahub
ahub.check_docker()
ahub.start_service('nginx')
ahub.start_service('certbot')
ahub.start_service('portainer')
ahub.start_service('scheduler')
ahub.start_service('aadauth')
ahub.start_service('gui')

ahub.check_certificate()

ahub.get_nginx_status()

ahub.stop_service('nginx')
ahub.stop_service('certbot')
ahub.stop_service('portainer')
ahub.stop_service('redis')
ahub.stop_service('scheduler')
ahub.stop_service('aadauth')
ahub.stop_service('gui')

ahub.get_nodes()
ahub.update_nginx()





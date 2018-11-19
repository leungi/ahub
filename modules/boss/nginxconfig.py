import re
from base64 import urlsafe_b64encode


def create_config(nodes):
    config = open('templates/nginx_template.conf', mode='r').read()
    upstream_template = open('templates/upstream_template.conf', mode="r").read()
    location_template = open('templates/location_template.conf', mode="r").read()
    tab = "    "

    upstream = []
    location = []
    for n in nodes:
        # Upstream server part
        insert = upstream_template.replace("#NODE", n)
        for s in [1 * tab + s for s in re.split("\n", insert)]:
            upstream.append(s)
        # Location part
        insert = location_template.replace("#NODE", n)
        for s in [2 * tab + s for s in re.split("\n", insert)]:
            location.append(s)

    config = config.replace('#INSERTUPSTREAM', "\n".join(upstream))
    config = config.replace('#INSERTLOCATION', "\n".join(location))
    config_enc = urlsafe_b64encode(config.encode('utf-8'))

    open('test.txt', 'w').write(config)

    return {"config": config, "config_enc": config_enc}

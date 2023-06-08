from typing import NamedTuple
import json
import base64
from os import environ


class ERSite(NamedTuple):
    host: str
    token: str
    show_track_days: int
    delay_days: int
    
class PublicSite(NamedTuple):
    name: str
    er_sites: list
    


SERVER_TYPE = environ.get('SERVERTYPE')
FRAMEWORK = environ.get('FRAMEWORK')


if SERVER_TYPE and FRAMEWORK and FRAMEWORK == 'Zappa':
    pass
else:
    with open('zappa_settings.json') as f:
        environment = json.load(f)['local']['environment_variables']
    for k,v in environment.items():
        environ[k] = str(v)

SUBJECTS_BUCKET = environ.get('SUBJECTS_BUCKET')
AWS_REGION = environ.get('AWS_REGION')

ER_TOKEN = environ.get('ER_TOKEN', '')
ER_HOST = environ.get('ER_HOST', '')
ER_PUBLIC_NAME = environ.get('ER_PUBLIC_NAME', '')

ER_HOST_CONFIG = environ.get('ER_HOST_CONFIG', '')
SERVER_URL = environ.get('SERVER_URL', 'http://localhost')
LOGIN_TOKEN = environ.get('LOGIN_TOKEN', '')
SUBJECTS_FOLDER = environ.get("SUBJECTS_FOLDER")
SHOW_TRACK_DAYS = 30
DELAY_DAYS = 0

PUBLIC_SITES = {}

def load_settings():
    if not ER_HOST_CONFIG:
        er_site = ERSite(ER_HOST, ER_TOKEN, SHOW_TRACK_DAYS, DELAY_DAYS)
        PUBLIC_SITES[ER_PUBLIC_NAME] = PublicSite(ER_PUBLIC_NAME, [er_site,])
        return
    
    host_config = base64.b64decode(ER_HOST_CONFIG)
    host_config = json.loads(host_config)

    for name, sites in host_config.items():
        er_sites = []
        for site in sites:
            show_track_days = site.get("show_track_days", SHOW_TRACK_DAYS)
            delay_days = site.get("delay_days", DELAY_DAYS)
            er_sites.append(ERSite(site['er_host'], site['er_token'], show_track_days, delay_days))
        PUBLIC_SITES[name] = PublicSite(name, er_sites)

load_settings()

import json
from os import environ


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
ER_TOKEN = environ.get('ER_TOKEN')
ER_HOST = environ.get('ER_HOST')
SERVER_URL = environ.get('SERVER_URL', 'http://localhost')
LOGIN_TOKEN = environ.get('LOGIN_TOKEN')
SUBJECTS_FOLDER = environ.get("SUBJECTS_FOLDER")

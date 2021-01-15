import os

SUBJECTS_BUCKET = os.getenv('SUBJECTS_BUCKET', 'bucket')
AWS_REGION = os.getenv('AWS_REGION', 'eu-central-1')
ER_TOKEN = os.getenv('ER_TOKEN')
ER_HOST = os.getenv('ER_HOST')
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost')
LOGIN_TOKEN = os.getenv('LOGIN_TOKEN')

import json

DEBUG = True
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

SECRET_KEY = 'SUPERSECRETKEY!'

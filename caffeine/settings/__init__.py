# -*- coding: utf-8; mode: python -*-

import sys
import logging
import coloredlogs

from os.path import join, abspath, dirname

from milieu import Environment


env = Environment()

SELF = sys.modules[__name__]


LOCAL_PORT = 5000
PORT = env.get_int('PORT', LOCAL_PORT)


# Identifying environment
LOCAL = PORT is LOCAL_PORT

# used for indicating where static files live in
ENVIRONMENT = {
    'production': 'pro',
    'development': 'dev',
}[env.get('CAFFEINE_ENVIRONMENT', 'development')]

# Detecting environment
DEBUG = LOCAL

# HTTP
HOST = env.get("HOST") or '127.0.0.1'
DOMAIN = env.get("DOMAIN") or 'localhost:{0}'.format(PORT)
SCHEME = env.get('SCHEME') or ('localhost' not in DOMAIN and 'https://' or 'http://')
LOG_LEVEL_NAME = (env.get('LOG_LEVEL') or 'INFO').upper()

# Database-related
SQLALCHEMY_DATABASE_URI = env.get('SQLALCHEMY_DATABASE_URI')
REDIS_URI = env.get_uri("REDIS_URI") or 'redis://localhost:6379'

# Filesystem
LOCAL_FILE = lambda *path: abspath(join(dirname(__file__), '..', '..', *path))

# Security
SECRET_KEY = env.get("SECRET_KEY")
WORKER_ADDRESS = env.get("WORKER_ADDRESS") or 'tcp://127.0.0.1:4200'

API_TOKEN_EXPIRATION_TIME = 60 * 60 * 12  # 12 hours in seconds

UPLOAD_PATH = env.get('CAFFEINE_UPLOAD_PATH') or 'inbox'
UPLOADED_FILE = lambda *path: join(UPLOAD_PATH, *path)

ACCESS_RESTRICTED_TO_EMAILS = [
    'gabriel@nacaolivre.org',     # Gabriel
    'cs.thevamp@gmail.com',       # Caius
    'mgoodwin87@gmail.com',       # Peege
    'raleigh.thevamp@gmail.com',  # Raleigh
    'ys.thevamp@gmail.com'        # YS
    'alscardoso@gmail.com',       # Café
]

absurl = lambda *path: "{0}{1}/{2}".format(
    SCHEME, DOMAIN, "/".join(path).lstrip('/'))

APP_URL = lambda *path: absurl('app', *path)
GOOGLE_ANALYTICS_CODE = env.get('GOOGLE_ANALYTICS_CODE') or 'UA-83260600-1'
GOOGLE_LOGIN_REDIRECT_URI = env.get('GOOGLE_LOGIN_REDIRECT_URI')
GOOGLE_LOGIN_CLIENT_ID = env.get('GOOGLE_LOGIN_CLIENT_ID')
GOOGLE_LOGIN_CLIENT_SECRET = env.get('GOOGLE_LOGIN_CLIENT_SECRET')
GOOGLE_LOGIN_REDIRECT_SCHEME = env.get('GOOGLE_LOGIN_REDIRECT_SCHEME') or 'https'
GOOGLE_LOGIN_SCOPES = ','.join([
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
])

AWS_ACCESS_KEY_ID = env.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env.get('AWS_SECRET_ACCESS_KEY')

if LOCAL:
    from .local import setup_localhost
    setup_localhost(SELF)
else:
    LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME)

    for logger in [None, 'caffeine', 'caffeine.worker', 'werkzeug']:
        logger = logging.getLogger()
        logger.setLevel(LOG_LEVEL)

    coloredlogs.install(level=LOG_LEVEL)

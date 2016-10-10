#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file sets up the default environment variables for working in
# local environment.

# The reason for this is that in production the app MUST work
# seamlessly after certain required environment variables are set.

# This file is an example of ALL those essential variables.
import os
from os.path import abspath, dirname, join

local_file = lambda *path: join(abspath(dirname(__file__)), *path)
project_file = lambda *path: local_file('..', *path)
root_file = lambda *path: project_file('..', *path)


DEFAULT_DB = 'mysql://root@localhost/caffeine'


def setup_localhost(settings):
    # Relational Database

    # REDIS
    # ~~~~~

    # Example of REDIS_URI for localhost:
    #   redis://localhost:6379
    #
    # Example of REDIS_URI for *PRODUCTION*:
    #   redis://redis-server-hostname:6379/verylongpasswordhash

    settings.REDIS_URI = 'redis://localhost:6379'
    settings.SESSION_SECRET_KEY = os.urandom(8).encode('hex')
    settings.STATIC_BASE_URL = '//localhost:5000/dist'
    settings.SQLALCHEMY_DATABASE_URI = DEFAULT_DB
    settings.SECRET_KEY = 'pxBnKDuVYNnwwFMUG26lZZfA84juTbJCXESuxED5ETE='

    settings.GOOGLE_LOGIN_REDIRECT_SCHEME = 'http'
    settings.GOOGLE_LOGIN_REDIRECT_URI = 'http://localhost:5000/oauth/callback'
    settings.GOOGLE_LOGIN_CLIENT_ID = "660201149701-nf35ri04q6cctmr39kjsh2onc6l8t1u9.apps.googleusercontent.com"
    settings.GOOGLE_LOGIN_CLIENT_SECRET = "sBMYG1ckEE9aluDTyexFETgs",
    settings.WORKER_ADDRESS = 'tcp://127.0.0.1:4200'

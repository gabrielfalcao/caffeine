# -*- coding: utf-8 -*-
import os
import re
import json as pyjson
import redis

import logging
import coloredlogs
from plant import Node
from caffeine import settings
from cryptography.fernet import Fernet
from datetime import date, time, datetime


def slugify(string):
    return re.sub(r'\W+', '_', string.strip()).lower()


def get_redis_connection():
    return redis.StrictRedis()


def sanitize_mailbox_name(name):
    found = re.match(r'^[_\w]+$', name)
    if found:
        return found.group(0)


def force_unicode(string):
    if not isinstance(string, unicode):
        return unicode(string, errors='ignore')

    return string


def configure_logging(level_name):
    logging.Logger.manager.loggerDict.clear()
    level = getattr(logging, bytes(level_name), b'DEBUG')

    logger = logging.getLogger()
    logger.handlers = []
    coloredlogs.install(level=level)


def json_converter(value):
    date_types = (datetime, date, time)
    if isinstance(value, date_types):
        value = value.isoformat()

    return str(value)


class json(object):

    @staticmethod
    def dumps(data, **kw):
        kw['default'] = json_converter
        kw['sort_keys'] = True
        return pyjson.dumps(data, **kw)

    @staticmethod
    def loads(*args, **kw):
        return pyjson.loads(*args, **kw)


def generate_encryption_key():
    return Fernet.generate_key()


def get_symmetrical_cypher(key):
    return Fernet(key)


def get_upload_node():
    return Node(settings.UPLOAD_PATH)


def sanitize_file_name(name):
    _, name = os.path.split(name)
    title, extension = os.path.splitext(name)
    return "".join([slugify(title), extension])

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import json
import logging
import traceback
import email.message

from flask import Flask, Response, request, redirect, g
from flask_googlelogin import GoogleLogin

from caffeine import settings
from caffeine.mailing import EmailMessage
from caffeine.util import configure_logging
from caffeine.util import get_symmetrical_cypher
from caffeine.workers import WorkerClient

COLORED_LOGS_LEVEL = os.environ.get('COLORED_LOGS_LEVEL')

if COLORED_LOGS_LEVEL:
    configure_logging(COLORED_LOGS_LEVEL)

COOKIE_NAME = 'caffeine_token'


class Application(Flask):
    def __init__(self, app_node):
        super(Application, self).__init__(
            __name__,
            static_folder=app_node.dir.join('static/dist'),
            template_folder=app_node.dir.join('templates'),
            static_url_path='/dist',
        )
        self.config.from_object('caffeine.settings')
        self.app_node = app_node
        self.secret_key = os.environ.get('SECRET_KEY')
        self.google = GoogleLogin(self)
        self.secret_key = settings.SECRET_KEY
        self.workers = WorkerClient(settings.WORKER_ADDRESS)

    def json_handle_weird(self, obj):
        if isinstance(obj, email.message.Message):
            return EmailMessage(obj).to_dict()

        logging.warning("failed to serialize %s", obj)
        return bytes(obj)

    def json_response(self, data, code=200, headers={}):
        headers = headers.copy()
        headers['Content-Type'] = 'application/json'
        payload = json.dumps(data, indent=2, default=self.json_handle_weird)
        r = Response(payload, status=code, headers=headers)
        return self.inject_token_in_response(r)

    def get_json_request(self):
        try:
            data = json.loads(request.data)
        except ValueError:
            logging.exception(
                "Trying to parse json body in the %s to %s",
                request.method, request.url,
            )
            data = {}

        return data

    def handle_exception(self, e):
        tb = traceback.format_exc(e)
        logging.error(tb)
        return self.json_response({'error': 'bad-request', 'traceback': tb}, code=400)

    def get_mail_path(self, name):
        path = self.config['MAIL_PATH_TEMPLATE'].format(name)
        return path

    @property
    def crypto(self):
        key = self.config['SECRET_KEY']
        cypher = get_symmetrical_cypher(key)
        return cypher

    def encrypt(self, data):
        return self.crypto.encrypt(bytes(data))

    def decrypt(self, data):
        if not data:
            return ''

        try:
            return self.crypto.decrypt(bytes(data))
        except Exception:
            return data

    def redirect_with_auth_cookie(self, url, value):
        response = redirect(url)
        kw = {}
        if value:
            value = self.encrypt(value)
        else:
            kw['expires'] = 0

        response.set_cookie(COOKIE_NAME, value, **kw)
        return response

    def inject_cookie_in_response(self, response, cookie):
        response.set_cookie(COOKIE_NAME, cookie)
        return response

    def inject_token_in_response(self, response):
        response.set_cookie(COOKIE_NAME, self.encrypt(self.get_cookie_token()) or g.token or '')
        return response

    def get_cookie_token(self):
        raw = request.cookies.get(COOKIE_NAME)
        return self.decrypt(raw)

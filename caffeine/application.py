#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import logging

from plant import Node
from flask import render_template

from caffeine.http import Application

node = Node(__file__)
server = Application(node)

RESTFUL_TOKEN_REGEX = re.compile(r'^Bearer:\s*(\S+)\s*$')

DEFAULT_IMAGE_PATH = node.dir.join('static/src/views/favicon-96.png')

logger = logging.getLogger('caffeine')


def parse_token(string):
    if not string:
        return

    found = RESTFUL_TOKEN_REGEX.search(string)
    if found:
        return found.group(1)


@server.route("/")
def index():
    return render_template('index.html')

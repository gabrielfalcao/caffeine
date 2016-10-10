# -*- coding: utf-8 -*-
import time
from datetime import datetime
from caffeine import conf
from flask import render_template, request
from tumbler import tumbler, json_response

route = tumbler.module(__name__)


@route.get('/')
def index():
    return render_template("index.html", **{
        'cache_flag': '-'.join([str(time.time())]),
        'absolute_url': conf.get_full_url,
        'user_token': request.cookies.get('carpentry_token') or ''
    })


@route.get('/api/projects')
def projects():
    return json_response([
        {
            "name": "Foo",
            "description": "The foo of the bar",
            "tags": ["test", "local"],
            "url": "http://foo.co",
            "last_build": datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"),
        },
        {
            "name": "Bar",
            "description": "The bar whence the foo belongs",
            "tags": ["example", "local"],
            "url": "http://bar.foo",
            "last_build": datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"),
        },
    ], 200)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import re
import json
import hashlib
import logging
import functools
import mimetypes
from datetime import datetime
from plant import Node
from flask import render_template, request, g, Response, redirect

from caffeine.http import Application

from caffeine.util import sanitize_file_name
from caffeine.util import get_upload_node

from caffeine.models import User
from caffeine.models import Track

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


def authenticated(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if g.user:
            return func(g.user, *args, **kw)

        auth = request.headers.get('Authorization') or ''
        token = parse_token(auth) or server.get_cookie_token()
        user = User.from_caffeine_token(token)

        if not user:
            msg = 'invalid token {0}'.format(token)
            logger.warning(msg)
            return server.json_response({'message': msg}, 401)

        if not user.is_authorized:
            msg = 'user exists but its email is not authorized: {0}'.format(user.email)
            logger.critical(msg)
            return server.json_response({'message': msg}, 401)

        g.user = user
        g.token = token
        return func(user, *args, **kw)

    return wrapper


@server.before_request
def prepare_user():
    g.user = User.from_caffeine_token(server.get_cookie_token())
    g.token = server.get_cookie_token()
    # connect to workers pipeline


@server.route("/api/user")
@authenticated
def api_user(user):
    return server.json_response(user.to_dictionary())


@server.route("/api/track/<int:track_id>", methods=['GET'])
@authenticated
def api_get_track(user, track_id):
    track = Track.find_one_by(id=track_id)
    if not track:
        return server.json_response({'message': 'track not found: {0}'.format(track_id)}, code=404)

    return server.json_response(track.to_dictionary())


@server.route("/api/track/<int:track_id>", methods=['PATCH'])
@authenticated
def api_edit_track(user, track_id):
    track = Track.find_one_by(id=track_id)
    if not track:
        return server.json_response({'message': 'track not found: {0}'.format(track_id)}, code=404)

    if track.user_id != user.id:
        return server.json_response({
            'message': 'cannot edit a track that you did not upload'
        }, code=400)

    data = server.get_json_request()

    track.update_fields(data)

    server.workers.request_job({
        'track_id': track_id
    })
    return server.json_response(track.to_dictionary())


@server.route("/api/track/<int:track_id>", methods=['PUT'])
@authenticated
def api_reprocess_track(user, track_id):
    track = Track.find_one_by(id=track_id)
    server.workers.request_job({
        'track_id': track_id
    })
    return server.json_response(track.to_dictionary())


@server.route("/api/track/<int:track_id>", methods=['DELETE'])
@authenticated
def api_delete_track(user, track_id):
    track = Track.find_one_by(id=track_id)
    if not track:
        return server.json_response({'message': 'track not found: {0}'.format(track_id)}, code=404)

    if track.user_id != user.id:
        return server.json_response({
            'message': 'cannot edit a track that you did not upload'
        }, code=400)

    track.delete()
    return server.json_response(track.to_dictionary())


@server.route("/api/tracks", methods=['POST'])
@authenticated
def api_tracks(user):
    upload_node = get_upload_node()
    tracks = []
    for name, obj in request.files.items():
        safe = sanitize_file_name(name)
        existing = Track.find_one_by(filename=safe, user_id=user.id)
        destination = upload_node.join(safe)
        destination_dir, filename = os.path.split(destination)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        obj.save(destination)
        if existing:
            data = existing.to_dictionary()
            data['status'] = 'already exists'
            track = existing
        else:
            track = Track.create(
                user_id=user.id,
                filename=safe,
                download_path=destination,
            )

            data = track.to_dictionary()
            data['status'] = 'saved'

        _, track.title = os.path.split(destination)
        track.download_path = destination
        track.save()
        server.workers.request_job({
            'track_id': track.id
        })
        tracks.append(data)

    return server.json_response({
        'tracks': tracks
    })


@server.route("/api/artwork/<int:track_id>", methods=['PUT'])
@authenticated
def api_change_artwork(user, track_id):
    upload_node = get_upload_node()
    obj = request.files['artwork']

    track = Track.find_one_by(id=track_id)

    if not track:
        return server.json_response({'message': 'track not found: {0}'.format(track_id)}, code=404)

    if track.user_id != user.id:
        return server.json_response({
            'message': 'cannot edit a track that you did not upload'
        }, code=400)

    _, extension = os.path.splitext(obj.name)
    name = "".join([hashlib.sha1(track.download_path).hexdigest(), extension])
    destination = upload_node.join(name)
    destination_dir, filename = os.path.split(destination)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    obj.save(destination)
    track.artwork_path = destination
    track.save()

    return server.json_response({
        'track': track.to_dictionary()
    })


@server.route("/api/tracks", methods=['GET'])
@authenticated
def api_get_tracks(user):
    return server.json_response({
        'tracks': [t.to_dictionary() for t in Track.all()]
    })


@server.route("/")
def index():
    server.workers.connect()
    return render_template('index.html')


@server.route("/admin")
def admin():
    server.workers.connect()
    return render_template('admin.html')


@server.route("/unauthorized")
def unauthorized():
    if g.user and g.user.is_authorized:
        return server.redirect_with_auth_cookie('/', '')

    return render_template('unauthorized.html', user=g.user)


@server.route('/admin')
def login():
    if g.token:
        return server.redirect_with_auth_cookie('/', g.token)

    url = server.google.login_url(redirect_uri=server.config['GOOGLE_LOGIN_REDIRECT_URI'])
    return server.redirect_with_auth_cookie(url, g.token)


@server.route('/track/<int:track_id>/image')
@authenticated
def download_track_image(user, track_id):
    track = Track.find_one_by(id=track_id)
    physical_path = track.artwork_path

    if not physical_path or not os.path.exists(physical_path):
        logger.warning('invalid image path: %s', physical_path)
        physical_path = DEFAULT_IMAGE_PATH

    try:
        data = open(physical_path, 'rb').read()
    except Exception:
        logger.exception('failed to load image: %s', physical_path)
        return Response('image not found', status=404)

    guessed, _ = mimetypes.guess_type(physical_path)
    return Response(data, content_type=guessed)


@server.route('/track/<int:track_id>/download')
@authenticated
def download_track_download(user, track_id):
    track = Track.find_one_by(id=track_id)
    data = open(track.download_path, 'rb').read()
    guessed, _ = mimetypes.guess_type(track.download_path)
    return Response(data, content_type=guessed or 'application/octet-stream')


@server.route('/logout')
def logout():
    if g.user:
        g.user.reset_token()

    return server.redirect_with_auth_cookie('/', '')


@server.route('/oauth/callback', methods=['POST', 'GET'])
@server.google.oauth2callback
def oauth_callback(token, userinfo, next='/'):
    email = userinfo.get('email')
    if not email:
        return render_template('unauthorized.html', status=401)

    user = User.get_or_create(
        email=email,
    )

    user.google_id = userinfo['id']
    user.name = userinfo.get('name', '')
    user.email = email
    user.avatar = userinfo.get('picture')
    user.json_metadata = json.dumps(userinfo)
    if user.is_authorized:
        user.activated_at = datetime.utcnow()
        user.activated_at = None

    else:
        return redirect('/unauthorized')

    user.save()
    token = user.reset_token()
    logger.info('GOOGLE USER AUTHENTICATED: {0}'.format(json.dumps(userinfo, indent=2)))

    return server.redirect_with_auth_cookie('/', token.get_value())

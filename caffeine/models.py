# -*- coding: utf-8 -*-
import os
import re
import uuid
import hashlib
import logging
import datetime
import sqlalchemy as db

from dateutil.parser import parse as parse_date

from caffeine import settings
from caffeine.orm import Model, metadata, DefaultForeignKey, PrimaryKey


logger = logging.getLogger('caffeine.models')


def slugify(string):
    return re.sub(r'\W+', '', string).lower()


class User(Model):
    table = db.Table(
        'user', metadata,
        PrimaryKey(),
        db.Column('name', db.UnicodeText),
        db.Column('username', db.String(64)),
        db.Column('email', db.String(128), unique=True),
        db.Column('google_id', db.String(128), unique=True),
        db.Column('avatar', db.UnicodeText),
        db.Column('json_metadata', db.UnicodeText),
        db.Column('is_authorized', db.Boolean),
        db.Column('activated_at', db.DateTime, nullable=True, default=None),
        db.Column('created_at', db.DateTime, default=datetime.datetime.utcnow),
    )

    def __repr__(self):
        return 'User(id={}, email="{}", google_id="{}")'.format(self.id, self.email, self.google_id)

    @classmethod
    def get_bot_user(cls):
        return cls.get_or_create(
            google_id=hashlib.sha512(settings.SECRET_KEY).hexdigest(),
            name=hashlib.sha512(settings.SECRET_KEY).hexdigest(),
            username='BOT',
            email='bot@{0}'.format(settings.DOMAIN),
        )

    @property
    def bot(self):
        return self.google_id == hashlib.sha512(settings.SECRET_KEY).hexdigest()

    @property
    def is_active(self):
        return self.activated_at is not None

    @property
    def is_authorized(self):
        return self.email in settings.ACCESS_RESTRICTED_TO_EMAILS

    def get_token(self):
        # TODO: make a SQL query instead of retrieving all tokens
        for token in CaffeineToken.from_user(self):
            if token.is_valid():
                return token

    def reset_token(self):
        token = CaffeineToken.create(
            user_id=self.id,
            token=uuid.uuid4().hex
        )
        return token

    def to_dictionary(self):
        data = self.to_dict()
        data.pop('created_at', None)
        data['bot'] = self.bot
        data['is_active'] = self.is_active
        return data

    @classmethod
    def from_caffeine_token(self, value):
        if not value:
            return

        return CaffeineToken.retrieve_user(value)


class CaffeineToken(Model):
    table = db.Table(
        'caffeine_token', metadata,
        PrimaryKey(),
        DefaultForeignKey('user_id', 'user.id'),
        db.Column('token', db.String(32)),
        db.Column('created_at', db.DateTime, default=datetime.datetime.utcnow),

    )

    def is_valid(self):
        now = datetime.datetime.utcnow()
        delta = now - parse_date(self.created_at)
        return delta.seconds < settings.API_TOKEN_EXPIRATION_TIME

    def get_value(self):
        return self.token or b''

    def get_user(self):
        return User.find_one_by(id=self.user_id)

    @classmethod
    def from_token(cls, value):
        token = cls.find_one_by(token=value)
        if not token:
            return

        if not token.is_valid():
            logger.warning('attempt to retrieve user from an expired token: %s', token)
            return

        return token

    @classmethod
    def from_user(cls, user):
        return cls.find_by(user_id=user.id)

    @classmethod
    def retrieve_user(cls, value):
        token = cls.from_token(value)
        if not token:
            logger.warning('attempt to retrieve user from an invalid token: %s', value)
            return

        return token.get_user()


class Playlist(Model):
    table = db.Table(
        'playlist', metadata,
        PrimaryKey(),
        DefaultForeignKey('user_id', 'user.id'),
        db.Column('title', db.UnicodeText),
        db.Column('description', db.UnicodeText),
    )


class Track(Model):
    table = db.Table(
        'track', metadata,
        PrimaryKey(),
        DefaultForeignKey('user_id', 'user.id'),
        db.Column('filename', db.Unicode(128)),
        db.Column('title', db.Unicode(30)),
        db.Column('artist', db.Unicode(30)),
        db.Column('genre', db.Unicode(100)),
        db.Column('album', db.Unicode(30)),
        db.Column('id3_json_metadata', db.UnicodeText),

        # can be file:///var/uploads/path-to-file.mp3 or s3://bucket/path/to/file
        db.Column('download_uri', db.UnicodeText),
        db.Column('artwork_uri', db.UnicodeText),
        # /srv/uploads
        db.Column('download_path', db.UnicodeText),
        db.Column('artwork_path', db.UnicodeText),
    )

    def __repr__(self):
        return '<Track(id={0}, download_path={1})>'.format(self.id, self.download_path)

    def get_artwork_url(self):
        url = settings.absurl('/track/{0}/image'.format(self.id))
        return url

    def get_download_url(self):
        return settings.absurl('/track/{0}/download'.format(self.id))

    def to_dictionary(self):
        data = self.to_dict()
        data['download_url'] = self.get_download_url()
        data['artwork_url'] = self.get_artwork_url()
        owner = User.find_one_by(id=self.user_id)
        data['user'] = owner and owner.to_dictionary()
        return data

    def delete(self):
        if os.path.exists(self.download_path):
            os.unlink(self.download_path)

        if self.artwork_path and os.path.exists(self.artwork_path):
            os.unlink(self.artwork_path)

        return super(Track, self).delete()

    def update_fields(self, data):
        title = data.get('title') or self.title
        artist = data.get('artist') or self.artist
        album = data.get('album') or self.album
        genre = data.get('genre') or self.genre

        self.title = title
        self.artist = artist
        self.album = album
        self.genre = genre
        self.save()

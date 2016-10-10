# -*- coding: utf-8 -*-

from __future__ import unicode_literals


import json
import signal
import gevent
import logging
import zmq.green as zmq

from plant import Node

from gevent.pool import Pool
from gevent.event import Event

from caffeine.mp3 import MP3
from caffeine.models import Track

logger = logging.getLogger('caffeine.worker')


WORKERS_BY_LABEL = {}


def get_worker_class_by_label(label):
    return WORKERS_BY_LABEL.get(label)


class MetaWorker(type):
    def __init__(cls, name, bases, attrs):
        def get_meta_member(name):
            return getattr(cls, name, attrs.get(name))

        super(MetaWorker, cls).__init__(name, bases, attrs)

        label = get_meta_member('label')
        WORKERS_BY_LABEL[label] = cls


class WorkerClient(object):
    def __init__(self, worker_address):
        self.worker_address = worker_address
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)

    def connect(self):
        self.socket.connect(self.worker_address)
        logger.info('connected to {0}'.format(self.worker_address))

    def request_job(self, job):

        logger.info('submitting job %s', job)
        self.socket.send_json(job)


class Worker(object):
    __metaclass__ = MetaWorker

    label = 'worker'
    action = 'process jobs'

    def __init__(self, concurrency=4, pull_bind_address=None):
        signal.signal(signal.SIGABRT | signal.SIGTERM, self.exit_gracefully)
        self.concurrency = concurrency
        self.context = zmq.Context()
        self.poller = zmq.Poller()
        self.socket = self.context.socket(zmq.PULL)

        self.allowed_to_run = Event()
        self.allowed_to_run.set()
        self.pool = Pool(concurrency)
        self.pull_bind_address = pull_bind_address

    def __repr__(self):
        template = u'{0}(pull_bind_address="{1}" concurrency={2})'
        return template.format(self.__class__.__name__, self.pull_bind_address, self.concurrency)

    def should_run(self):
        return self.allowed_to_run.is_set()

    def stop(self):
        self.allowed_to_run.clear()

    def exit_gracefully(self, *args, **kw):
        self.stop()
        self.context.destroy()

    def poll_socket(self):
        sockets = dict(self.poller.poll())
        available = sockets[self.socket] == zmq.POLLIN
        if available:
            return self.socket

    def consume_job(self):
        socket = self.poll_socket()
        if not socket:
            logger.info('socket not ready: {0}'.format(self.pull_bind_address))
            return

        return socket.recv_json()

    def loop_once(self):
        logger.info('{0} is ready to {1} on demand'.format(self.label, self.action))

        job = self.consume_job()

        if not job:
            logger.info('no request to {1} was received for {0}'.format(self.label, self.action))
            gevent.sleep()
            return

        self.pool.spawn(self.do_execute, job)

    def do_execute(self, job):
        try:
            return self.execute(**job)
        except Exception as e:
            logger.warning('error "{1}" occurred, rolling back job {0}'.format(job, e))
            return self.do_rollback(e, job)

    def do_rollback(self, exception, job):
        try:
            result = self.rollback(exception, job)
            logger.info('rollback successfull: "{0}": {1}'.format(job, result))

        except Exception:
            logger.exception('failed to rollback job: {0}'.format(job))
            return

        return result

    def mainloop(self):
        # listen for jobs in the zmq PULL socket
        self.socket.bind(self.pull_bind_address)
        self.poller.register(self.socket, zmq.POLLIN)
        logger.info('ZMQ PULL BIND at: {0}'.format(self.pull_bind_address))
        while self.should_run():
            self.loop_once()
            gevent.sleep(1)

    def run(self, pull_bind_address=None):
        if pull_bind_address:
            self.pull_bind_address = pull_bind_address

        self.mainloop()

    def spawn(self, pull_bind_address=None):
        return gevent.spawn(self.run, pull_bind_address)

    def rollback(self, exception, job):
        logger.exception('failed to rollback {0}'.format(job))

    def execute(self, **kw):
        raise NotImplementedError


class ExtractID3(Worker):
    label = 'id3-extractor'
    action = 'process mp3 files'

    def execute(self, track_id):
        track = Track.find_one_by(id=track_id)
        if not track:
            raise RuntimeError('could not find track: {0}'.format(track_id))

        logger.info('extracting ID3 information from: {0}...'.format(track.download_path))

        id3 = MP3(track.download_path)
        metadata = id3.to_dict()

        track.id3_json_metadata = json.dumps(metadata)
        track.title = metadata.get('title') or track.title
        track.artist = metadata.get('artist') or track.artist
        track.album = metadata.get('album') or track.album
        track.genre = metadata.get('genre') or track.genre
        track.save()

        logger.info('extracting image artwork from from: {0}...'.format(track.download_path))
        artwork = id3.get_artwork()

        if not artwork:
            logger.warning('track {} has no artwork'.format(track))
            return

        destination = Node(track.download_path).dir
        final_path = destination.join(artwork.filename)
        artwork.save(final_path)
        track.artwork_path = final_path
        track.save()
        logger.info(
            ('Done processing: {0}\n'
             '\n'
             'Title: {1}\n'
             'Artist: {2}\n'
             'Album: {3}\n'
             'Genre: {4}\n').format(track.download_path, track.title, track.artist, track.album, track.genre))

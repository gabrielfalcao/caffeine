# -*- coding: utf-8 -*-

import json

from plant import Node
from carbontube import Phase, Pipeline
from carbontube.storage import RedisStorageBackend

from caffeine.mp3 import MP3
from caffeine.models import Track


class TrackProcessingPhase(Phase):
    def execute(self, instructions):
        track_id = instructions['track_id']
        track = Track.find_one_by(id=track_id)
        if not track:
            raise RuntimeError('could not find track: {0}'.format(track_id))

        self.process_track(track)
        return instructions


class LoadID3Info(TrackProcessingPhase):
    job_type = 'process-id3'

    def process_track(self, track):
        id3 = MP3(track.download_path)
        metadata = id3.to_dict()

        track.id3_json_metadata = json.dumps(metadata)
        track.title = metadata.get('title') or track.title
        track.artist = metadata.get('artist') or track.artist
        track.album = metadata.get('album') or track.album
        track.save()


class LoadID3Artwork(TrackProcessingPhase):
    job_type = 'process-artwork'

    def process_track(self, track):
        id3 = MP3(track.download_path)
        artwork = id3.get_artwork()

        if not artwork:
            raise RuntimeError('track {} has no artwork'.format(track))

        destination = Node(track.download_path).dir
        final_path = artwork.save(destination.path)
        track.artwork_path = final_path
        track.save()


class Example1(Pipeline):
    name = 'id3-extractor'

    phases = [
        LoadID3Info,
        LoadID3Artwork,
    ]

    def initialize(self):
        self.backend = RedisStorageBackend(self.name, redis_uri='redis://127.0.0.1:6379')

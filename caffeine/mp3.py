import os
import io
import hashlib
import inspect

import eyed3

from plant import Node


class MP3(object):
    def __init__(self, path):
        self.path = path
        self.id3 = eyed3.load(path)

    def get_images(self):
        if not self.id3:
            return []

        if not self.id3.tag:
            return []

        return [MP3Image(self, i) for i in self.id3.tag.images]

    def to_dict(self):
        if not self.id3:
            return {}

        if not self.id3.tag:
            return {}

        data = dict(map(lambda (k, v): (k, getattr(v, 'name', v)), filter(lambda (k, v): not k.startswith('_') and (isinstance(v, basestring) or hasattr(v, 'name')), inspect.getmembers(self.id3.tag))))
        return data

    def get_artwork(self):
        images = self.get_images()
        if not images:
            return

        return images[0]


class MP3Image(object):
    def __init__(self, mp3, image_frame):
        self.id3 = mp3
        self.data = image_frame.image_data
        self.mime_type = image_frame.mime_type
        self.original_filename = image_frame.makeFileName()
        _, self.file_extension = os.path.splitext(self.original_filename)

    @property
    def filename(self):
        return "".join([hashlib.sha1(self.data).hexdigest(), self.file_extension.lower()])

    def save(self, destination_path):
        dst_node = Node(destination_path).dir
        final_path = dst_node.join(self.filename)
        with io.open(final_path, 'wb') as fd:
            fd.write(self.data)

        return final_path

    def to_dict(self):
        return {
            'mime_type': self.mime_type,
            'filename': self.filename,
            'hexdata': self.data.encode('hex')
        }

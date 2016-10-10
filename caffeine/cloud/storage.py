import boto
import boto.s3.connection


class FileStorage(object):
    def __init__(self):
        self.connection = boto.connect_s3(
            host='objects-us-west-1.dream.io',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )

        self.buckets = BucketManager(self.connection)

    def for_tracks(self):
        return self.parent.connection.get_bucket('caffeine-tracks')

    def for_images(self):
        return self.parent.connection.get_bucket('caffeine-images')

    def store_track(self, source_path):
        pass

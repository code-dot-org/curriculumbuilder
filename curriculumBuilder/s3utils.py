from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage

StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')
MediaRootS3BotoStorage  = lambda: S3BotoStorage(location='media')
CurriculumRootS3BotoStorage  = lambda: S3BotoStorage(location='curriculum')


class CachedS3BotoStorage(StaticRootS3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        self.local_storage._save(name, content)
        super(CachedS3BotoStorage, self).save(name, self.local_storage._open(name))
        return name

    def get_available_name(self, name):
        """ Always overwrite existing file with the same name. """
        name = self._clean_name(name)
        return name
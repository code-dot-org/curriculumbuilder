from storages.backends.s3boto import S3BotoStorage, S3BotoStorageFile

# StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')
# MediaRootS3BotoStorage  = lambda: S3BotoStorage(location='media')
# CurriculumRootS3BotoStorage  = lambda: S3BotoStorage(location='curriculum')


class S3BotoStorageSafe(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        return super(S3BotoStorageSafe, self).__init__(*args, **kwargs)

    def isfile(self, name):
        try:
            name = self._normalize_name(self._clean_name(name))
            f = S3BotoStorageFile(name, 'rb', self)
            if not f.key:
                return False
            return True
        except:
            return False

    def isdir(self, name):
        return not self.isfile(name)

    def move(self, old_file_name, new_file_name, allow_overwrite=False):

        if self.exists(new_file_name):
            if allow_overwrite:
                self.delete(new_file_name)
            else:
                raise "The destination file '%s' exists and allow_overwrite is False" % new_file_name

        old_key_name = self._encode_name(self._normalize_name(self._clean_name(old_file_name)))
        new_key_name = self._encode_name(self._normalize_name(self._clean_name(new_file_name)))

        k = self.bucket.copy_key(new_key_name, self.bucket.name, old_key_name)

        if not k:
            raise "Couldn't copy '%s' to '%s'" % (old_file_name, new_file_name)

        self.delete(old_file_name)

    def makedirs(self, name):
        # i can't create dirs still
        pass

    def rmtree(self, name):
        name = self._normalize_name(self._clean_name(name))
        dirlist = self.bucket.list(self._encode_name(name))
        for item in dirlist:
            item.delete()

    def save(self, name, content):
        re = super(S3BotoStorageSafe, self).save(name, content)
        # key.copy(key.bucket, key.name, preserve_acl=True, metadata={'Content-Type': 'text/plain'})
        return re


StaticRootS3BotoStorage = lambda: S3BotoStorageSafe(location='static', file_overwrite=True)
StaticStagingS3BotoStorage = lambda: S3BotoStorageSafe(location='static_staging', file_overwrite=True)
MediaRootS3BotoStorage = lambda: S3BotoStorageSafe(location='media', file_overwrite=False)
CurriculumRootS3BotoStorage = lambda: S3BotoStorageSafe(location='curriculum', file_overwrite=True)
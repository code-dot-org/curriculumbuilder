from storages.backends.s3boto import S3BotoStorage

# Provide an implementation of S3BotoStorage that doesn't preload metadata.
# This speeds up several operations in certain contexts; see
# https://stackoverflow.com/a/21121924/1810460 for more details.
#
# We prefer to use this over globally setting AWS_PRELOAD_METADATA to False,
# because CollectFast depends on that being True.
class NoPreloadedMetadataS3BotoStorage(S3BotoStorage):
    preload_metadata = False

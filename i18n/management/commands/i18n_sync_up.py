# pylint: disable=missing-docstring,too-few-public-methods,no-self-use
import glob
import os
import subprocess

from django.core.management.base import BaseCommand
from distutils.dir_util import copy_tree

from i18n.management.utils import log, get_models_to_sync
from i18n.utils import I18nFileWrapper


class Command(BaseCommand):

    def handle(self, *args, **options):
        log("I18n Sync Step 2 of 4: Upload source strings to Crowdin")
        source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')
        upload_dir = os.path.join(I18nFileWrapper.static_dir(), 'upload')

        # Strings uploaded should include all source strings, some of which
        # will need to be redacted.
        copy_tree(source_dir, upload_dir)

        models_to_redact = [
            model for model in get_models_to_sync()
            if model.should_redact()
        ]

        # Redact all source files
        log("Redacting source files for %s" % ', '.join(model.__name__ for model in models_to_redact))
        for model in models_to_redact:
            filename = model.__name__ + ".json"
            source_path = os.path.join(source_dir, filename)
            destination_path = os.path.join(upload_dir, filename)
            plugins_path = os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")
            plugins = ",".join(glob.glob(plugins_path))
            subprocess.call([
                "redact", source_path,
                "-o", destination_path,
                "-p", plugins
            ])

        # Upload redacted source files to crowdin
        log("Uploading source files")
        subprocess.call([
            os.path.join(I18nFileWrapper.i18n_dir(), 'heroku_crowdin.sh'),
            "--config", os.path.join(I18nFileWrapper.i18n_dir(), "config", "crowdin.yml"),
            "upload sources"
        ])

# pylint: disable=missing-docstring
import glob
import os
import subprocess

from django.core.management.base import BaseCommand
from distutils.dir_util import copy_tree

from i18n.management.utils import log, get_models_to_sync
from i18n.utils import I18nFileWrapper


class Command(BaseCommand):
    source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')
    upload_dir = os.path.join(I18nFileWrapper.static_dir(), 'upload')

    def prepare_sources(self):
        """Gather all sources strings into upload directory"""
        copy_tree(self.source_dir, self.upload_dir)

    def redact_sources(self):
        """Redact within upload directory those sources for which it is enabled"""
        models_to_redact = [
            model for model in get_models_to_sync()
            if model.should_redact()
        ]

        log("Redacting source files for %s" %
            ', '.join(model.__name__ for model in models_to_redact))
        for model in models_to_redact:
            filename = model.__name__ + ".json"
            source_path = os.path.join(self.source_dir, filename)
            destination_path = os.path.join(self.upload_dir, filename)
            plugins_path = os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")
            plugins = ",".join(glob.glob(plugins_path))
            subprocess.call([
                "redact", source_path,
                "-o", destination_path,
                "-p", plugins
            ])

    @staticmethod
    def upload_sources():
        """Upload sources files to crowdin"""
        log("Uploading source files")
        subprocess.call([
            os.path.join(I18nFileWrapper.i18n_dir(), 'heroku_crowdin.sh'),
            "--config", os.path.join(I18nFileWrapper.i18n_dir(), "config", "crowdin.yml"),
            "upload sources"
        ])

    def handle(self, *args, **options):
        log("I18n Sync Step 2 of 4: Upload source strings to Crowdin")
        self.prepare_sources()
        self.redact_sources()
        self.upload_sources()

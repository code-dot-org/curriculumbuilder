# pylint: disable=missing-docstring,too-few-public-methods,no-self-use
import glob
import os
import subprocess

from django.core.management.base import BaseCommand

from i18n.management.utils import log
from i18n.utils import I18nFileWrapper


class Command(BaseCommand):

    def handle(self, *args, **options):
        log("I18n Sync Step 2 of 4: Upload source strings to Crowdin")
        source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')
        redacted_dir = os.path.join(I18nFileWrapper.static_dir(), 'redacted')

        if not os.path.exists(redacted_dir):
            os.makedirs(redacted_dir)

        # Redact all source files
        log("Redacting source files")
        for path in glob.glob(os.path.join(source_dir, '*')):
            filename = os.path.basename(path)
            destination = os.path.join(redacted_dir, filename)
            plugins_path = os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")
            plugins = ",".join(glob.glob(plugins_path))
            subprocess.call([
                "redact", path,
                "-o", destination,
                "-p", plugins
            ])

        # Upload redacted source files to crowdin
        log("Uploading source files")
        subprocess.call([
            os.path.join(I18nFileWrapper.i18n_dir(), 'heroku_crowdin.sh'),
            "--config", os.path.join(I18nFileWrapper.i18n_dir(), "config", "crowdin.yml"),
            "upload sources"
        ])

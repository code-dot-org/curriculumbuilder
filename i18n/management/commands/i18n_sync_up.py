import glob
import os
import subprocess

from i18n.utils import I18nFileWrapper
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')
        redacted_dir = os.path.join(I18nFileWrapper.static_dir(), 'redacted')

        if not os.path.exists(redacted_dir):
            os.makedirs(redacted_dir)

        # Redact all source files
        print("Redacting source files")
        for path in glob.glob(os.path.join(source_dir, '*')):
            filename = os.path.basename(path)
            destination = os.path.join(redacted_dir, filename)
            subprocess.call(["redact", path, "-o", destination])

        # Upload redacted source files to crowdin
        print("Uploading source files")
        subprocess.call([
            os.path.join(I18nFileWrapper.i18n_dir(), 'heroku_crowdin.sh'),
            "--config", os.path.join(I18nFileWrapper.i18n_dir(), "config", "crowdin.yml"),
            "upload sources"
        ])

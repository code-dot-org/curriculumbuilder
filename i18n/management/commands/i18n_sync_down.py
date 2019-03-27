# pylint: disable=missing-docstring,too-few-public-methods,no-self-use
import glob
import os
import subprocess

from django.core.management.base import BaseCommand

from i18n.management.utils import log, get_non_english_language_codes
from i18n.utils import I18nFileWrapper


class Command(BaseCommand):
    def handle(self, *args, **options):
        source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')
        translations_dir = os.path.join(I18nFileWrapper.static_dir(), 'translations')

        # Download translations from crowdin
        log("I18n Sync Step 3 of 4: Download translations from Crowdin")
        subprocess.call([
            os.path.join(I18nFileWrapper.i18n_dir(), 'heroku_crowdin.sh'),
            "--config", os.path.join(I18nFileWrapper.i18n_dir(), "config", "crowdin.yml"),
            "download"
        ])

        source_paths = glob.glob(os.path.join(source_dir, '*'))
        log("Restoring and uploading %s" % ", ".join(map(os.path.basename, source_paths)))
        log("For %s" % ", ".join(get_non_english_language_codes()))

        # Restore translations from source
        log("Restoring redacted translations from source")
        for locale in get_non_english_language_codes():
            for source_path in source_paths:
                filename = os.path.basename(source_path)
                translation_path = os.path.join(translations_dir, locale, filename)
                if not os.path.exists(translation_path):
                    continue
                plugins_path = os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")
                plugins = ",".join(glob.glob(plugins_path))
                subprocess.call([
                    'restore',
                    '-s', source_path,
                    '-r', translation_path,
                    '-o', translation_path,
                    '-p', plugins
                ])

        # Upload restored translation data to s3
        log("Uploading restored translations to S3")
        for locale in get_non_english_language_codes():
            for translation_path in glob.glob(os.path.join(translations_dir, locale, '*')):
                if not os.path.exists(translation_path):
                    continue
                filename = os.path.basename(translation_path)
                with open(translation_path) as translation_file:
                    dest_path = os.path.join('translations', locale, filename)
                    I18nFileWrapper.storage().save(dest_path, translation_file)

# pylint: disable=missing-docstring,too-few-public-methods,no-self-use
import glob
import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

from i18n.management.utils import log
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

        # Restore translations from source
        log("Restoring redacted translations from source")
        for locale, _ in settings.LANGUAGES:
            if locale == settings.LANGUAGE_CODE:
                continue
            for source_path in glob.glob(os.path.join(source_dir, '*')):
                filename = os.path.basename(source_path)
                translation_path = os.path.join(translations_dir, locale, filename)
                if not os.path.exists(translation_path):
                    continue
                plugins_path = os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")
                plugins = ",".join(glob.glob(plugins_path))
                log("%s - restoring %s" % (locale, filename))
                subprocess.call([
                    'restore',
                    '-s', source_path,
                    '-r', translation_path,
                    '-o', translation_path,
                    '-p', plugins
                ])
            log("%s - finished" % locale)

        # Upload restored translation data to s3
        log("Uploading restored translations to S3")
        for locale, _ in settings.LANGUAGES:
            if locale == settings.LANGUAGE_CODE:
                continue
            for translation_path in glob.glob(os.path.join(translations_dir, locale, '*')):
                if not os.path.exists(translation_path):
                    continue
                filename = os.path.basename(translation_path)
                log("%s - uploading %s" % (locale, filename))
                with open(translation_path) as translation_file:
                    dest_path = os.path.join('translations', locale, filename)
                    I18nFileWrapper.storage().save(dest_path, translation_file)
            log("%s - finished" % locale)

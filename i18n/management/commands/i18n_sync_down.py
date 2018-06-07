import glob
import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from i18n.utils import I18nFileWrapper, print_clear


class Command(BaseCommand):
    def handle(self, *args, **options):
        source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')
        translations_dir = os.path.join(I18nFileWrapper.static_dir(), 'translations')
        num_locales = len(settings.LANGUAGES)

        # Download translations from crowdin
        print("Downloading translations")
        subprocess.call([
            os.path.join(I18nFileWrapper.i18n_dir(), 'heroku_crowdin.sh'),
            "--config", os.path.join(I18nFileWrapper.i18n_dir(), "crowdin.yml"),
            "download"
        ])

        # Restore translations from source
        print("Restoring translations")
        for source_path in glob.glob(os.path.join(source_dir, '*')):
            filename = os.path.basename(source_path)
            for index, (locale, _) in enumerate(settings.LANGUAGES):
                translation_path = os.path.join(translations_dir, locale, filename)
                if not os.path.exists(translation_path):
                    continue
                print_clear("%s - restoring %s (%s/%s)" % (filename, locale, index + 1, num_locales))
                subprocess.call([
                    'restore',
                    '-s', source_path,
                    '-r', translation_path,
                    '-o', translation_path
                ])
            print_clear("%s - finished" % filename)

        # Upload restored translation data to s3
        print("Uploading translations")
        for index, (locale, _) in enumerate(settings.LANGUAGES):
            for translation_path in glob.glob(os.path.join(translations_dir, locale, '*')):
                if not os.path.exists(translation_path):
                    continue
                filename = os.path.basename(translation_path)
                print_clear("%s - uploading %s (%s/%s)" % (locale, filename, index + 1, num_locales))
                with open(translation_path) as translation_file:
                    I18nFileWrapper.storage().save(os.path.join('translations', locale, filename), translation_file)
            print_clear("%s - finished" % locale)

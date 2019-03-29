# pylint: disable=missing-docstring
import glob
import os
import subprocess

from django.core.management.base import BaseCommand

from i18n.management.utils import log, get_non_english_language_codes, get_models_to_sync
from i18n.utils import I18nFileWrapper


class Command(BaseCommand):
    source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')
    translations_dir = os.path.join(I18nFileWrapper.static_dir(), 'translations')

    @staticmethod
    def download_translations():
        """Download translations from crowdin"""
        subprocess.call([
            os.path.join(I18nFileWrapper.i18n_dir(), 'heroku_crowdin.sh'),
            "--config", os.path.join(I18nFileWrapper.i18n_dir(), "config", "crowdin.yml"),
            "download"
        ])

    def restore_translations(self):
        """Restore translations from source"""
        # Only redacted content should be restored; otherwise, we're running a
        # markdown formatter over content that may or may not be markdown.
        models_to_restore = [
            model for model in get_models_to_sync()
            if model.should_redact()
        ]
        log("Restoring redacted translations for %s" %
            ', '.join(model.__name__ for model in models_to_restore))
        log("For %s" % ", ".join(get_non_english_language_codes()))
        for locale in get_non_english_language_codes():
            for model in models_to_restore:
                filename = model.__name__ + ".json"
                source_path = os.path.join(self.source_dir, filename)
                translation_path = os.path.join(self.translations_dir, locale, filename)
                if not os.path.exists(translation_path):
                    log("Could not find %s to restore" % translation_path)
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

    def upload_translations(self):
        """Upload restored translation data to s3"""
        source_paths = glob.glob(os.path.join(self.source_dir, '*'))
        log("Uploading restored translations to S3: %s" %
            ", ".join(map(os.path.basename, source_paths)))
        for locale in get_non_english_language_codes():
            for translation_path in glob.glob(os.path.join(self.translations_dir, locale, '*')):
                if not os.path.exists(translation_path):
                    log("Could not find %s to upload" % translation_path)
                    continue
                filename = os.path.basename(translation_path)
                with open(translation_path) as translation_file:
                    dest_path = os.path.join('translations', locale, filename)
                    I18nFileWrapper.storage().save(dest_path, translation_file)

    def handle(self, *args, **options):
        log("I18n Sync Step 3 of 4: Download and process translations")
        self.download_translations()
        self.restore_translations()
        self.upload_translations()

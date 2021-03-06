# pylint: disable=missing-docstring
import glob
import os
import subprocess

from django.core import management
from django.core.management.base import BaseCommand

from i18n.management.utils import log, get_non_english_locale_names, get_models_to_sync
from i18n.utils import I18nFileWrapper
from i18n.management.crowdin import Crowdin


class Command(BaseCommand):
    source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')

    @staticmethod
    def download_translations():
        """Download translations from crowdin"""
        Crowdin().download_translations()

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
        log("For %s" % ", ".join(get_non_english_locale_names()))
        missing_files_to_restore = []
        for locale_name in get_non_english_locale_names():
            for model in models_to_restore:
                filename = model.__name__ + ".json"
                source_path = os.path.join(self.source_dir, filename)
                translation_path = os.path.join(
                    I18nFileWrapper.locale_dir_absolute(locale_name),
                    filename
                )
                if not os.path.exists(translation_path):
                    missing_files_to_restore.append(translation_path)
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
        if len(missing_files_to_restore) > 0:
            log("Could not restore: %s" % missing_files_to_restore)

        log("Compiling Django translations")
        management.call_command("compilemessages")

    def upload_translations(self):
        """Upload restored translation data to s3"""
        source_paths = glob.glob(os.path.join(self.source_dir, '*'))
        log("Uploading restored translations to S3: %s" %
            ", ".join(map(os.path.basename, source_paths)))
        missing_files_to_upload = []
        for locale_name in get_non_english_locale_names():
            translations_glob = os.path.join(I18nFileWrapper.locale_dir_absolute(locale_name), '*')
            for translation_path in glob.glob(translations_glob):
                if not os.path.exists(translation_path):
                    missing_files_to_upload.append(translation_path)
                    continue
                filename = os.path.basename(translation_path)
                with open(translation_path) as translation_file:
                    dest_path = os.path.join(I18nFileWrapper.locale_dir(locale_name), filename)
                    I18nFileWrapper.storage().save(dest_path, translation_file)
        if len(missing_files_to_upload) > 0:
            log("Could not upload: %s" % missing_files_to_upload)

    def handle(self, *args, **options):
        log("I18n Sync Step 3 of 4: Download and process translations")
        try:
            self.download_translations()
            self.restore_translations()
            self.upload_translations()
        except Exception as err:
            log(err)
            raise

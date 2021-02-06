# pylint: disable=missing-docstring
import glob
import os
import json

from django.core import management
from django.core.management.base import BaseCommand
from django.utils.translation import to_locale
from django.core.files.storage import FileSystemStorage

from i18n.management.crowdin import Crowdin
from i18n.management.utils import log, get_non_english_language_codes
from i18n.utils import I18nFileWrapper


class Command(BaseCommand):

    # Retrieves all django.po files from Crowdin and
    # saves them locally
    def download_message_file(self):
        # Download changes!
        for language_code in get_non_english_language_codes():

            locale = to_locale(language_code)
            language_dir = I18nFileWrapper.locale_dir_absolute(locale)
            if not os.path.exists(language_dir):
                os.makedirs(language_dir)

            # Load existing etags from previous sync, if it exists.
            # Note that here we're using locale_dir and not locale_dir_absolute; we want to
            # specifically retrieve the etags from wherever they are persisted, even if that's not
            # the local filesystem.
            etags = {}
            etags_path = os.path.join(I18nFileWrapper.locale_dir(locale), "crowdin_etags.json")
            if I18nFileWrapper.storage().exists(etags_path):
                log("loading existing etags from %s" % etags_path)
                with I18nFileWrapper.storage().open(etags_path, 'r') as etags_file:
                    etags = json.load(etags_file)

            if language_code not in etags:
                etags[language_code] = {}

            filepath = "django.po"
            etag = etags[language_code].get(filepath, None)
            response = Crowdin().export_file(filepath, language_code, etag=etag)
            if response.status_code == 200:

                # Update the etag for this file, for use in the next sync
                etags[language_code][filepath] = response.headers['etag']

                # Persist the contents of the file.
                # Although we have access to the I18nFileWrapper here and could persist the
                # contents directly to S3, we actually need them on the local filesystem so we
                # can restore them; other parts of the sync process will handle uploading the
                # files to S3.
                full_filepath = os.path.join(language_dir, filepath)
                if not os.path.exists(os.path.dirname(full_filepath)):
                    os.makedirs(os.path.dirname(full_filepath))

                with open(full_filepath, 'w') as _file:
                    _file.write(response.content)
            elif response.status_code == 304:
                # 304 means there's no change (based on the etag), so we don't need to do
                # anything
                pass
            else:
                raise Exception(
                    "Cannot handle response code {} for file \"{}\" in language \"{}\"".format(
                        response.status_code, filepath, language_code
                    )
                )

            storage_etags_path = os.path.join(str(I18nFileWrapper.storage().location), I18nFileWrapper.locale_dir(locale))
            if isinstance(I18nFileWrapper.storage(), FileSystemStorage) and not os.path.exists(storage_etags_path):
                os.makedirs(storage_etags_path)
            with I18nFileWrapper.storage().open(etags_path, 'w') as etags_file:
                json.dump(etags, etags_file, sort_keys=True, indent=4)

    def handle(self, *args, **options):
        log("Checking for updates in django.po")
        try:
            self.download_message_file()
            management.call_command("compilemessages")
        except Exception as err:
            log(err)
            raise

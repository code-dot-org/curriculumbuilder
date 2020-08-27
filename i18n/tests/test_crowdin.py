# pylint: disable=protected-access
"""
Contains tests for the Crowdin class, which provides access to the Crowdin API for the I18n sync
"""
import os
import json

from django.test import TestCase, override_settings
from django.utils.translation import to_locale
from mock import patch
from requests import Response

from i18n.management.crowdin import Crowdin, ETAGS_FILENAME
from i18n.management.utils import CHANGES_JSON
from i18n.utils import I18nFileWrapper


@override_settings(I18N_STORAGE='django.core.files.storage.FileSystemStorage')
@override_settings(I18N_STORAGE_LOCATION='i18n/static')
class CrowdinTest(TestCase):
    """
    Basic tests for the Crowdin class
    """
    def setUp(self):
        self.crowdin = Crowdin()
        self.crowdin._project_info = {
            "files": [
                {
                    "node_type": "file",
                    "name": "top-level file",
                },
                {
                    "node_type": "directory",
                    "name": "top-level directory",
                    "files": [
                        {
                            "node_type": "file",
                            "name": "nested file",
                        },
                        {
                            "node_type": "directory",
                            "name": "nested directory",
                            "files": [
                                {
                                    "node_type": "file",
                                    "name": "innermost file",
                                },
                            ]
                        }
                    ]
                }
            ]
        }

    def test_flattens_filepaths(self):
        """
        Test the ability of the 'gather filepaths' method to flatten the nested
        structure returned by Crowdin
        """
        filepaths = self.crowdin.filepaths()
        expected = [
            'top-level file',
            'top-level directory/nested file',
            'top-level directory/nested directory/innermost file',
        ]
        self.assertEqual(filepaths, expected)

    def test_updates_etags(self):
        """
        Test that the 'download translations' process will also persist the
        updated etags for each file in each language
        """
        export_file_response = Response()
        export_file_response.status_code = 200
        export_file_response.headers['etag'] = "brand new etag"
        export_file_response._content = ""

        with patch.object(self.crowdin, 'export_file', return_value=export_file_response):
            self.crowdin.download_translations()

        language_dir = I18nFileWrapper.locale_dir(to_locale('es-mx'))
        etags_path = os.path.join(language_dir, ETAGS_FILENAME)
        with I18nFileWrapper.storage().open(etags_path, 'r') as etags_file:
            etags = json.load(etags_file)
            self.assertEqual(
                etags["es-mx"]["top-level directory/nested directory/innermost file"],
                "brand new etag"
            )
            self.assertEqual(etags["es-mx"]["top-level directory/nested file"], "brand new etag")
            self.assertEqual(etags["es-mx"]["top-level file"], "brand new etag")

        export_file_response.headers['etag'] = "even newer etag"
        with patch.object(self.crowdin, 'export_file', return_value=export_file_response):
            self.crowdin.download_translations()

        with I18nFileWrapper.storage().open(etags_path, 'r') as etags_file:
            etags = json.load(etags_file)
            self.assertEqual(
                etags["es-mx"]["top-level directory/nested directory/innermost file"],
                "even newer etag"
            )
            self.assertEqual(etags["es-mx"]["top-level directory/nested file"], "even newer etag")
            self.assertEqual(etags["es-mx"]["top-level file"], "even newer etag")

    def test_saves_changes(self):
        """
        Test that the 'download translations' process will also persist a list
        of changed files in each language
        """
        def mock_export_file(filepath, _language, etag=None):
            """
            mock the Crowdin.export_file method to return a '304 not modified'
            for one of our expeced filepaths, and a '200 OK' for the others, so
            our expected list of changes can exclude exactly that file
            """
            response = Response()
            response.headers['etag'] = etag
            if filepath == 'top-level directory/nested file':
                response.status_code = 304
            else:
                response.status_code = 200
            response._content = ""
            return response

        with patch.object(self.crowdin, 'export_file', mock_export_file):
            self.crowdin.download_translations()
        with open(CHANGES_JSON, 'r') as changes_json:
            changes = json.load(changes_json)
            self.assertEqual(changes.values()[0], [
                'top-level file',
                'top-level directory/nested directory/innermost file',
            ])

    def test_downloads_translations(self):
        """
        Test that the 'download translations' process will also persist the
        updated files
        """
        def mock_export_file(filepath, _language, etag=None):
            """
            mock the Crowdin.export_file method to return unique content for
            each path, so we can verify that the right content was written to
            the right path.
            """
            response = Response()
            response.headers['etag'] = etag
            response.status_code = 200
            response._content = "Content for '%s'" % filepath
            return response

        with patch.object(self.crowdin, 'export_file', mock_export_file):
            self.crowdin.download_translations()

        language_dir = I18nFileWrapper.locale_dir(to_locale('es-mx'))
        with open(os.path.join(language_dir, 'top-level file'), 'r') as _file:
            self.assertEqual(_file.read(), "Content for 'top-level file'")

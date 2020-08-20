"""
Provides the Crowdin class, for all kinds of interaction with Crowdin data.
"""

import json
import os
import logging

import requests

from django.utils.translation import to_locale

from .utils import get_non_english_language_codes, CHANGES_JSON
from ..utils import I18nFileWrapper

API_KEY = os.environ.get('CROWDIN_API_KEY')
ETAGS_FILENAME = "crowdin_etags.json"
PROJECT_ID = 'curriculumbuilder'


# Crowdin sometimes uses four-letter language codes consistent with the language codes we use
# internally, but sometimes uses other formats for its language codes. This constant provides a
# mapping from our codes to Crowdin's for those cases for which they differ.
CROWDIN_LANGUAGE_CODES = {
    'hi-in': 'hi',
    'it-it': 'it',
    'pl-pl': 'pl',
    'sk-sk': 'sk',
    'th-th': 'th',
    'in-tl': 'in'
}


class Crowdin(object):
    """
    This class provides access to data stored on Crowdin, via the Crowdin API.

    See https://support.crowdin.com/api/ for API Reference
    See https://github.com/code-dot-org/code-dot-org/blob/staging/lib/cdo/crowdin/project.rb for
    ruby implemntation
    """
    def __init__(self):
        self._project_info = None
        self._filepaths = None

        self.logger = logging.getLogger('i18n')

    @staticmethod
    def request(method, endpoint, params=None, headers=None):
        """
        Make a request to the Crowdin API for this project, using the specified method, endpoint,
        and parameteres.
        """
        if params is None:
            params = {}

        if API_KEY is None:
            raise Exception(
                "no API key found. Please make sure the CROWDIN_API_KEY environment variable is set"
            )

        base_uri = "https://api.crowdin.com/api/project/" + PROJECT_ID
        default_params = {
            "key": API_KEY,
            "json": True
        }

        params = dict(default_params.items() + params.items())
        return getattr(requests, method)(
            base_uri + "/" + endpoint,
            params=params,
            headers=headers
        )

    def info(self):
        """
        Retrieve project info from https://support.crowdin.com/api/info/. Cached.
        """
        if self._project_info is None:
            self.logger.debug("Retrieving project info from Crowdin")
            self._project_info = self.request('post', "info").json()
        return self._project_info

    def filepaths(self):
        """
        Retrieve list of all files currently uploaded to this project. Files will be presented as a
        flat list of full filepaths.
        """
        if self._filepaths is None:
            self.logger.debug("Retrieving list of files from Crowdin")
            self._filepaths = []

            def gather_filepaths(filenames, path=""):
                """
                Recursively iterate through the files and directories returned by the Crowdin API
                call, gathering the results into a flat list.
                """
                for filename in filenames:
                    name = filename["name"]
                    filepath = os.path.join(path, name)
                    if filename["node_type"] == "directory":
                        subfilenames = filename["files"]
                        gather_filepaths(subfilenames, filepath)
                    elif filename["node_type"] == "file":
                        self._filepaths.append(filepath)

            gather_filepaths(self.info()["files"])

        return self._filepaths

    def export_file(self, filepath, language, etag=None):
        """
        Download the specified file in the specified language from crowdin. The etag argument can be
        used to skip downloading a file if there are no changes.

        See https://support.crowdin.com/api/export-file/
        """
        if language in CROWDIN_LANGUAGE_CODES:
            language = CROWDIN_LANGUAGE_CODES[language]

        params = {
            'file': filepath,
            'language': language
        }

        headers = {}
        if etag is not None:
            headers["If-None-Match"] = etag

        return self.request('get', 'export-file', params=params, headers=headers)

    def download_translations(self):
        """
        Download all files with new translation activity since our last sync in all languages. In
        addition to downloading updates to the files themselves, will also update our "etags" file,
        which we use to identify file changes for future syncs, and will return a dictionary
        containing a list of changed files for each language
        """

        changes = dict()

        # Download changes!
        language_codes = get_non_english_language_codes()
        for i, language_code in enumerate(get_non_english_language_codes()):
            self.logger.debug("%s: %s/%s", language_code, i + 1, len(language_codes))

            language_dir = I18nFileWrapper.locale_dir_absolute(to_locale(language_code))
            if not os.path.exists(language_dir):
                os.makedirs(language_dir)

            # Load existing etags from previous sync, if it exists
            etags = {}
            etags_path = os.path.join(language_dir, ETAGS_FILENAME)
            if os.path.exists(etags_path):
                self.logger.debug("loading existing etags from %s", etags_path)
                with I18nFileWrapper.storage().open(etags_path, 'r') as etags_file:
                    etags = json.load(etags_file)

            changes[language_code] = []
            if language_code not in etags:
                etags[language_code] = {}

            for filepath in self.filepaths():
                etag = etags[language_code].get(filepath, None)
                response = self.export_file(filepath, language_code, etag=etag)
                if response.status_code == 200:
                    # Add the file to the list of files changed in this sync
                    changes[language_code].append(filepath)

                    # Update the etag for this file, for use in the next sync
                    etags[language_code][filepath] = response.headers['etag']

                    # Persist the contents of the file
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

            self.logger.debug("%s files have changes", len(changes[language_code]))
            with open(etags_path, 'w') as etags_file:
                json.dump(etags, etags_file, sort_keys=True, indent=4)

        self.logger.info(
            "%s changed files downloaded across %s languages",
            sum(len(files) for files in changes.values()),
            len(language_codes)
        )

        # Persist changes to file, so they can be referenced by the "publish" step
        with open(CHANGES_JSON, 'w') as changes_json:
            json.dump(changes, changes_json, sort_keys=True, indent=4)
        return changes

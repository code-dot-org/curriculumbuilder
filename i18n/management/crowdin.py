# pylint: disable=superfluous-parens
"""
Provides the Crowdin class, for all kinds of interaction with Crowdin data.
"""

import json
import os
import logging

import requests

PROJECT_ID = 'curriculumbuilder'
API_KEY = os.environ.get('CROWDIN_API_KEY')


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
        self._etags_json = "/tmp/cb_etags.json"
        self._changes_json = "/tmp/cb_changes.json"

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    @staticmethod
    def request(method, endpoint, params=None, headers=None):
        """
        Make a request to the Crowdin API for this project, using the specified method, endpoint,
        and parameteres.
        """
        if params is None:
            params = {}

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

    def languages(self):
        """
        Retrieve list of all languages enabled for this project.
        """
        return self.info()["languages"]

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
        which we use to identify file changes for future syncs, and our "changes" file, which we
        will use in the sync out to identify which files got changed this sync.
        """
        # Load existing etags from previous sync
        etags = {}
        if os.path.exists(self._etags_json):
            with open(self._etags_json, 'r') as etags_file:
                etags = json.load(etags_file)

        changes = dict()

        # Download changes!
        for i, language in enumerate(self.languages()):
            language_code = language["code"]

            self.logger.debug("{} ({}): {}/{}".format(
                language['name'], language_code, i, len(self.languages())
            ))
            if i > 0 and i % (len(self.languages()) / 5) == 0:
                self.logger.info("~{}% complete ({}/{})".format(
                    (i * 100 / len(self.languages())), i, len(self.languages())
                ))

            download_dir = os.path.join("/tmp/cbsync", language_code)
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            changes[language_code] = []
            if language_code not in etags:
                etags[language_code] = {}

            for filepath in self.filepaths():
                etag = etags[language_code].get(filepath, None)
                response = self.export_file(filepath, language_code, etag=etag)
                if response.status_code == 200:
                    # Add the file to our list of changed files
                    changes[language_code].append(filepath)

                    # Update the etag
                    etags[language_code][filepath] = response.headers['etag']

                    # Download the contents of the file
                    with open(os.path.join(download_dir, filepath), 'w') as _file:
                        _file.write(response.content)
                elif response.status_code == 304:
                    # 304 means there's no change (based on the etag), so we don't need to do
                    # anything
                    pass
                else:
                    raise Exception(
                        "Cannot handle response code {} for file \"{}\" in language \"{}\"".format(
                            response.status_code, filepath, language
                        )
                    )

            self.logger.debug("{} files have changes".format(len(changes[language_code])))
            with open(self._changes_json, 'w') as changes_file:
                json.dump(changes, changes_file, sort_keys=True, indent=4)
            with open(self._etags_json, 'w') as etags_file:
                json.dump(etags, etags_file, sort_keys=True, indent=4)

        self.logger.info("{} changed files downloaded across {} languages".format(
            sum(len(files) for files in changes.items()), len(self.languages())
        ))

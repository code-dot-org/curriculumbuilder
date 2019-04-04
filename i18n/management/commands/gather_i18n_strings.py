# pylint: disable=missing-docstring,too-few-public-methods,no-self-use
import json
import os
import subprocess

from django.core import management
from django.core.management.base import BaseCommand

from i18n.management.utils import log, get_models_to_sync
from i18n.utils import I18nFileWrapper


class Command(BaseCommand):
    def handle(self, *args, **options):
        log("I18n Sync Step 1 of 4: Gather source strings from models")
        source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)

        for model in get_models_to_sync():
            strings = model.gather_strings()
            outpath = os.path.abspath(os.path.join(source_dir, model.__name__ + ".json"))
            with open(outpath, 'w') as outfile:
                json.dump(strings, outfile, indent=4, sort_keys=True)
            log("Gathered %s strings from %s into %s" % (len(strings), model.__name__, outpath))

        # Gather strings for translation in html files.
        # For some reason makemessages won't create the locale/ directory but will create
        # the subdirectories
        template_string_path = "locale"
        if not os.path.exists(template_string_path):
            os.mkdir(template_string_path)
        management.call_command("makemessages",
                                "--locale", "en",
                                "--ignore", "src*",
                                "--no-obsolete")
        log("Gathered template strings")

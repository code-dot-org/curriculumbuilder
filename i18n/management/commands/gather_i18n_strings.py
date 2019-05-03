# pylint: disable=missing-docstring
import json
import os

from django.core import management
from django.core.management.base import BaseCommand

from i18n.management.utils import log, get_models_to_sync
from i18n.utils import I18nFileWrapper


class Command(BaseCommand):
    source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')

    def gather_model_strings(self):
        if not os.path.exists(self.source_dir):
            os.makedirs(self.source_dir)

        for model in get_models_to_sync():
            strings = model.gather_strings()
            outpath = os.path.abspath(os.path.join(self.source_dir, model.__name__ + ".json"))
            with open(outpath, 'w') as outfile:
                json.dump(strings, outfile, indent=4, sort_keys=True)
            log("Gathered %s strings from %s into %s" % (len(strings), model.__name__, outpath))

    def gather_template_strings(self):
        """Gather strings for translation in html files."""
        # For some reason makemessages won't create the locale/ directory but
        # will create the subdirectories
        template_string_path = "locale"
        if not os.path.exists(template_string_path):
            os.mkdir(template_string_path)
        management.call_command("makemessages",
                                "--locale", "en",
                                "--ignore", "src*",
                                "--no-obsolete")
        os.rename("locale/en/LC_MESSAGES/django.po", os.path.join(self.source_dir, "django.po"))
        log("Gathered template strings")

    def handle(self, *args, **options):
        log("I18n Sync Step 1 of 4: Gather source strings from models")
        self.gather_model_strings()
        self.gather_template_strings()

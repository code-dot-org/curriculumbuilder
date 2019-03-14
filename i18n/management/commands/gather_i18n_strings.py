import json
import os
import subprocess

import django.apps

from django.core import management
from django.core.management.base import BaseCommand
from i18n.models import Internationalizable
from i18n.utils import I18nFileWrapper


class Command(BaseCommand):
    def handle(self, *args, **options):
        source_dir = os.path.join(I18nFileWrapper.static_dir(), 'source')
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)

        for model in django.apps.apps.get_models():
            # We care about models that:
            #   extend the InternationalizablePage models defined by this module
            #   are not proxy models (used by Django Admin for editing)
            is_internationalizable = issubclass(model, Internationalizable)
            is_not_proxy = not model._meta.proxy
            if (is_internationalizable and is_not_proxy):
                strings = model.gather_strings()
                outpath = os.path.abspath(os.path.join(source_dir, model.__name__ + ".json"))
                with open(outpath, 'w') as outfile:
                    json.dump(strings, outfile, indent=4, sort_keys=True)

        # Gather strings for translation in html files.
        # For some reason makemessages won't create the locale/ directory but will create
        # the subdirectories
        subprocess.call(["mkdir", "locale/"])
        management.call_command("makemessages", "-l en")

from i18n.models import InternationalizablePage
from django.core.management.base import BaseCommand, CommandError

import django.apps
import json
import os

class Command(BaseCommand):
    def handle(self, *args, **options):
        staticfiles = os.path.join(os.path.dirname(__file__), '../../static')

        for model in django.apps.apps.get_models():
            if (issubclass(model, InternationalizablePage)):
                strings = model.gather_strings()
                outpath = os.path.abspath(os.path.join(staticfiles, model.__name__ + ".json"))
                with open(outpath, 'w') as outfile:
                    json.dump(strings, outfile, indent=4, sort_keys=True)

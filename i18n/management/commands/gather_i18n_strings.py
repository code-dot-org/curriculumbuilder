from i18n.models import Internationalizable
from i18n.utils import I18nFileWrapper
from django.core.management.base import BaseCommand, CommandError

import django.apps


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model in django.apps.apps.get_models():
            # We care about models that:
            #   extend the InternationalizablePage models defined by this module
            #   are not proxy models (used by Django Admin for editing)
            is_internationalizable = issubclass(model, Internationalizable)
            is_not_proxy = not model._meta.proxy
            if (is_internationalizable and is_not_proxy):
                strings = model.gather_strings()
                I18nFileWrapper.write_source(model.__name__, strings)

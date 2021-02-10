# pylint: disable=missing-docstring
import glob
import os
import json

from django.core import management
from django.core.management.base import BaseCommand

from i18n.management.crowdin import Crowdin
from i18n.management.utils import log

class Command(BaseCommand):

    def handle(self, *args, **options):
        log("Checking for updates in django.po")
        try:
            Crowdin().download_translations(["django.po"])
            management.call_command("compilemessages")
        except Exception as err:
            log(err)
            raise

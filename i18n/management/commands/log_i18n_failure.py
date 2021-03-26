# pylint: disable=missing-docstring
from i18n.management.utils import log

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Used by the i18n sync to alert that not all steps finished successfully.
    See bin/sync_i18n.sh for context.
    """
    def handle(self, *args, **options):
        log("<!subteam^S017CFFHHT9|foundations-team> ERROR: I18n Sync encountered a problem and did not complete")
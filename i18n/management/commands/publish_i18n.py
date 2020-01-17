# pylint: disable=missing-docstring
import datetime
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation

from i18n.management.utils import log, get_models_to_sync

def can_publish_model(model):
    return hasattr(model, 'publish') or hasattr(model, 'publish_pdfs')

class Command(BaseCommand):

    models = [
        model for model in get_models_to_sync()
        if can_publish_model(model)
    ]

    language_codes = [
        language_code for language_code, _ in settings.LANGUAGES
        if language_code != settings.LANGUAGE_CODE
    ]

    def publish_models(self):
        """
        Execute the publish and publish_pdfs methods on all translatable models
        that define them
        """
        log("Models to publish: %s" % ', '.join(model.__name__ for model in self.models))
        log("Languages to publish: %s" % ', '.join(self.language_codes))

        total_elapsed_time = 0
        for model_index, model in enumerate(self.models):
            name = model.__name__
            log("Publishing %s (%s/%s)" % (name, model_index + 1, len(self.models)))
            objects = model.get_i18n_objects()
            total = objects.count()
            success_count = 0
            start_time = time.time()

            for obj in objects.all():
                if not obj.should_be_translated:
                    continue

                for language_code in self.language_codes:
                    translation.activate(language_code)
                    if hasattr(obj, 'publish'):
                        list(obj.publish(silent=True))
                    if language_code in settings.LANGUAGE_GENERATE_PDF and hasattr(obj, 'publish_pdfs'):
                        list(obj.publish_pdfs(silent=True))
                success_count += 1

            end_time = time.time()
            elapsed_time = (end_time - start_time)
            total_elapsed_time += elapsed_time

            log("%s/%s %s objects published in %s" % (
                success_count, total, name, datetime.timedelta(seconds=int(elapsed_time))
            ))

        log("Publishing %s models in %s languages finished in %s (average of ~%s per language)" % (
            len(self.models), len(self.language_codes),
            datetime.timedelta(seconds=int(total_elapsed_time)),
            datetime.timedelta(seconds=int(total_elapsed_time/len(self.language_codes)))
        ))

    def handle(self, *args, **options):
        log("I18n Sync Step 4 of 4: Publish translated content to S3")
        self.publish_models()

# pylint: disable=missing-docstring,too-few-public-methods,no-self-use
import datetime
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation

from i18n.management.utils import log, get_models_to_sync

class Command(BaseCommand):
    def can_publish_model(self, model):
        return hasattr(model, 'publish') or hasattr(model, 'publish_pdfs')

    def handle(self, *args, **options):
        log("I18n Sync Step 4 of 4: Publish translated content to S3")

        models = [
            model for model in get_models_to_sync()
            if self.can_publish_model(model)
        ]
        log("Models to publish: %s" % ', '.join(model.__name__ for model in models))

        language_codes = [
            language_code for language_code, _ in settings.LANGUAGES
            if language_code != settings.LANGUAGE_CODE
        ]
        log("Languages to publish: %s" % ', '.join(language_codes))

        total_elapsed_time = 0
        for model_index, model in enumerate(models):
            name = model.__name__
            log("Publishing %s (%s/%s)" % (name, model_index + 1, len(models)))
            objects = model.get_i18n_objects()
            total = objects.count()
            success_count = 0
            start_time = time.time()

            for obj in objects.all():
                if not obj.should_be_translated:
                    continue

                for language_code in language_codes:
                    translation.activate(language_code)
                    if hasattr(obj, 'publish'):
                        list(obj.publish(silent=True))
                    if hasattr(obj, 'publish_pdfs'):
                        list(obj.publish_pdfs(silent=True))
                success_count += 1
            end_time = time.time()
            elapsed_time = (end_time - start_time)
            total_elapsed_time += elapsed_time

            log("%s/%s %s objects published in %s" % (
                success_count, total, name, datetime.timedelta(seconds=int(elapsed_time))
            ))

        log("Publishing %s models in %s languages finished in %s (average of ~%s per language" % (
            len(models), len(language_codes),
            datetime.timedelta(seconds=int(total_elapsed_time)),
            datetime.timedelta(seconds=int(total_elapsed_time/len(language_codes)))
        ))

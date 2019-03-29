# pylint: disable=missing-docstring,too-few-public-methods,no-self-use
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

        for model_index, model in enumerate(models):
            name = model.__name__
            log("Publishing %s (%s/%s)" % (name, model_index + 1, len(models)))
            objects = model.get_i18n_objects()
            total = objects.count()
            success_count = 0

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

            log("%s/%s %s objects published" % (success_count, total, name))

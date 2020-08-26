# pylint: disable=missing-docstring, broad-except
import datetime
import time
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation

from i18n.management.utils import log, get_models_to_sync, get_non_english_language_codes, CHANGES_JSON


def can_publish_model(model):
    return hasattr(model, 'publish') or hasattr(model, 'publish_pdfs')


class Command(BaseCommand):

    models = [
        model for model in get_models_to_sync()
        if can_publish_model(model)
    ]

    def __init__(self, *args, **kwargs):
        self.total_elapsed_time = 0
        self.total_pdf_generation_time = 0

        with open(CHANGES_JSON) as changes_json:
            self.changes = json.load(changes_json)

        super(Command, self).__init__(*args, **kwargs)

    def has_changes(self, language_code):
        # Because the published contents of a model include contents from other
        # models, we can't easily determine whether a specific model should be
        # published or not based on the changed files. So, we just determine
        # changes on a per-language (rather than per-language and also
        # per-model) basis. This should be sufficient for our needs given the
        # relatively low translation activity for this project, but we may need
        # to make this more sophisticated in the future if that changes.
        return len(self.changes[language_code]) > 0

    def publish_object(self, obj, language_code):
        translation.activate(language_code)

        if hasattr(obj, 'publish'):
            list(obj.publish(silent=True))

        if language_code in settings.LANGUAGE_GENERATE_PDF and hasattr(obj, 'publish_pdfs'):
            try:
                start_time = time.time()
                list(obj.publish_pdfs(silent=True))
                end_time = time.time()
                self.total_pdf_generation_time += (end_time - start_time)
            except Exception as err:
                log(err)
                log("PDF publishing failed %s in %s" % (obj.slug, language_code))

    def publish_models(self):
        """
        Execute the publish and publish_pdfs methods on all translatable models
        that define them
        """
        log("Models to publish: %s" % ', '.join(model.__name__ for model in self.models))
        log("Languages to publish: %s" % ', '.join(get_non_english_language_codes()))

        for model_index, model in enumerate(self.models):
            name = model.__name__
            objects = model.get_i18n_objects()
            total = objects.count()
            log("Publishing %s (%s/%s): %s objects" % (
                name,
                model_index + 1,
                len(self.models),
                total
            ))

            num_published = 0
            start_time = time.time()

            for language_code in get_non_english_language_codes():
                if not self.has_changes(language_code):
                    continue
                for obj in objects.all():
                    if not obj.should_be_translated:
                        continue
                    self.publish_object(obj, language_code)
                    num_published += 1

            end_time = time.time()

            elapsed_time = (end_time - start_time)
            self.total_elapsed_time += elapsed_time

            log("%s/%s %s objects published in %s" % (
                num_published,
                total,
                name,
                datetime.timedelta(seconds=int(elapsed_time))
            ))

    def report_final_times(self):
        total_non_pdf_generation_time = self.total_elapsed_time - self.total_pdf_generation_time
        num_languages = len(get_non_english_language_codes())
        log((
            "Publishing %s models in %s languages took %s total, %s not including PDF generation "
            "(average of ~%s per language). PDF generation took %s"
        ) % (
            len(self.models), len(get_non_english_language_codes()),
            datetime.timedelta(seconds=int(self.total_elapsed_time)),
            datetime.timedelta(seconds=int(total_non_pdf_generation_time)),
            datetime.timedelta(seconds=int(total_non_pdf_generation_time/num_languages)),
            datetime.timedelta(seconds=int(self.total_pdf_generation_time))
        ))

    def handle(self, *args, **options):
        log("I18n Sync Step 4 of 4: Publish translated content to S3")
        self.publish_models()
        self.report_final_times()

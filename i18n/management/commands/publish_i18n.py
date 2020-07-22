# pylint: disable=missing-docstring, broad-except
import datetime
import time
import multiprocessing

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation
from django import db

from i18n.management.utils import log, get_models_to_sync


def can_publish_model(model):
    return hasattr(model, 'publish') or hasattr(model, 'publish_pdfs')


def publish(obj):
    if not obj.should_be_translated:
        return

    pdf_generation_time = 0

    for language_code in Command.language_codes:
        translation.activate(language_code)
        if hasattr(obj, 'publish'):
            list(obj.publish(silent=True))
        # Temporary hack to turn off PDF generation while still directing users to the
        # translated pdfs if they exist
        if language_code in settings.LANGUAGE_GENERATE_PDF and hasattr(obj, 'publish_pdfs'):
            try:
                pdf_generation_start_time = time.time()
                list(obj.publish_pdfs(silent=True))
                pdf_generation_end_time = time.time()
                pdf_generation_time += pdf_generation_end_time - pdf_generation_start_time
            except Exception as err:
                log(err)
                log("PDF publishing failed %s in %s" % (obj.slug, language_code))

    return pdf_generation_time


class Command(BaseCommand):

    models = [
        model for model in get_models_to_sync()
        if can_publish_model(model)
    ]

    language_codes = [
        language_code for language_code, _ in settings.LANGUAGES
        if language_code != settings.LANGUAGE_CODE
    ]

    def __init__(self, *args, **kwargs):
        self.total_elapsed_time = 0
        self.total_pdf_generation_time = 0

        super(Command, self).__init__(*args, **kwargs)

    def publish_models(self):
        """
        Execute the publish and publish_pdfs methods on all translatable models
        that define them
        """
        log("Models to publish: %s" % ', '.join(model.__name__ for model in self.models))
        log("Languages to publish: %s" % ', '.join(self.language_codes))

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

            # By default, the spawned processes will attempt to reuse the existing database
            # connections, which will cause conflicts. To prevent this, we explicitly close all
            # database connections immediately before spawning the processes, which will force them
            # to each open their own connection.
            db.connections.close_all()

            start_time = time.time()
            results = multiprocessing.Pool(multiprocessing.cpu_count()).map(publish, objects.all())
            end_time = time.time()

            published_results = [result for result in results if result is not None]
            elapsed_time = (end_time - start_time)
            self.total_elapsed_time += elapsed_time
            self.total_pdf_generation_time += sum(published_results)

            log("%s/%s %s objects published in %s" % (
                len(published_results),
                total,
                name,
                datetime.timedelta(seconds=int(elapsed_time))
            ))

    def report_final_times(self):
        total_non_pdf_generation_time = self.total_elapsed_time - self.total_pdf_generation_time
        log((
            "Publishing %s models in %s languages took %s total, %s not including PDF generation "
            "(average of ~%s per language). PDF generation took %s"
        ) % (
            len(self.models), len(self.language_codes),
            datetime.timedelta(seconds=int(self.total_elapsed_time)),
            datetime.timedelta(seconds=int(total_non_pdf_generation_time)),
            datetime.timedelta(seconds=int(total_non_pdf_generation_time/len(self.language_codes))),
            datetime.timedelta(seconds=int(self.total_pdf_generation_time))
        ))

    def handle(self, *args, **options):
        log("I18n Sync Step 4 of 4: Publish translated content to S3")
        self.publish_models()
        self.report_final_times()

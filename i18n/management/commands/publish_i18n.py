# pylint: disable=missing-docstring, broad-except
import datetime
import time
import json
import multiprocessing

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation
from django import db

from i18n.management.utils import log, get_models_to_sync, get_non_english_language_codes, CHANGES_JSON


def can_publish_model(model):
    return hasattr(model, 'publish') or hasattr(model, 'publish_pdfs')


def publish_object_html(obj):
    if obj.should_be_translated and hasattr(obj, 'publish'):
        list(obj.publish(silent=True))


def publish_object_pdfs(obj):
    if obj.should_be_translated and hasattr(obj, 'publish_pdfs'):
        list(obj.publish_pdfs(silent=True))


class Command(BaseCommand):

    models = [
        model for model in get_models_to_sync()
        if can_publish_model(model)
    ]

    def __init__(self, *args, **kwargs):
        self.total_elapsed_time = 0
        self.pdf_publishing_time = 0
        self.html_publishing_time = 0
        self.pool = multiprocessing.Pool(multiprocessing.cpu_count())

        with open(CHANGES_JSON) as changes_json:
            self.changes = json.load(changes_json)

        super(Command, self).__init__(*args, **kwargs)

    def get_language_codes_with_changes(self):
        return [language_code for language_code
                in get_non_english_language_codes()
                if self.has_changes(language_code)]

    def has_changes(self, language_code):
        # Because the published contents of a model include contents from other models, we can't
        # easily determine whether a specific model should be published or not based on the changed
        # files. So, we just determine changes on a per-language (rather than per-language and also
        # per-model) basis. This should be sufficient for our needs given the relatively low
        # translation activity for this project, but we may need to make this more sophisticated in
        # the future if that changes.
        return len(self.changes.get(language_code, [])) > 0

    def publish_objects_in_language(self, objects, language_code):
        translation.activate(language_code)

        # By default, the spawned processes will attempt to reuse the existing database connections,
        # which will cause conflicts. To prevent this, we explicitly close all database connections
        # immediately before spawning the processes, which will force them to each open their own
        # connection.
        db.connections.close_all()

        start_time = time.time()
        self.pool.imap_unordered(publish_object_html, objects.all())
        end_time = time.time()
        self.html_publishing_time += (end_time - start_time)

        if language_code in settings.LANGUAGE_GENERATE_PDF:
            pdf_start_time = time.time()
            self.pool.imap_unordered(publish_object_pdfs, objects.all())
            pdf_end_time = time.time()
            self.pdf_publishing_time += (pdf_end_time - pdf_start_time)

    def publish_models(self):
        """
        Execute the publish and publish_pdfs methods on all translatable models
        that define them
        """
        log("Models to publish: %s" % ', '.join(model.__name__ for model in self.models))
        log("Languages to publish: %s" % ', '.join(self.get_language_codes_with_changes()))

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
            start_time = time.time()

            for language_code in self.get_language_codes_with_changes():
                self.publish_objects_in_language(objects.all(), language_code)

            end_time = time.time()
            elapsed_time = (end_time - start_time)
            self.total_elapsed_time += elapsed_time

            log("%s objects published in %s" % (
                name,
                datetime.timedelta(seconds=int(elapsed_time))
            ))

    def report_final_times(self):
        num_languages = len(self.get_language_codes_with_changes())
        log((
            "Publishing %s models in %s languages took %s total (average of ~%s per language)"
        ) % (
            len(self.models), num_languages,
            datetime.timedelta(seconds=int(self.total_elapsed_time)),
            datetime.timedelta(seconds=int(self.total_elapsed_time/num_languages)),
        ))
        log((
            "HTML Publishing took %s total (average of ~%s per language)"
        ) % (
            datetime.timedelta(seconds=int(self.html_publishing_time)),
            datetime.timedelta(seconds=int(self.html_publishing_time/num_languages)),
        ))
        log((
            "PDF Publishing took %s total (average of ~%s per language)"
        ) % (
            datetime.timedelta(seconds=int(self.pdf_publishing_time)),
            datetime.timedelta(seconds=int(self.pdf_publishing_time/num_languages)),
        ))

    def handle(self, *args, **options):
        log("I18n Sync Step 4 of 4: Publish translated content to S3")
        self.publish_models()
        self.report_final_times()

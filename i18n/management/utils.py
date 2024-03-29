"""
Helper methods for use during the i18n sync process
"""
import django.apps

from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.utils.translation import to_locale

from django_slack import slack_message

from i18n.models import Internationalizable

CHANGES_JSON = "/tmp/crowdin_sync_latest_changes.json"


def should_sync_model(model):
    """
    whether or not the given Django model is something the i18n sync should
    process. We care about models that:
        - extend the Internationalizable model defined by this module
        - are not proxy models (unless the model explicitly opts in to translation)
    """
    is_internationalizable = issubclass(model, Internationalizable)
    should_skip = model._meta.proxy and not getattr(model, 'translate_proxy', False)  # pylint: disable=protected-access
    return is_internationalizable and not should_skip


def get_models_to_sync():
    """Retrieve all models that should be processed by the i18n sync"""
    return [model for model in django.apps.apps.get_models() if should_sync_model(model)]


def get_non_english_language_codes():
    """
    Retrieve all language codes (ie "es-mx") for languages we need to process
    in the i18n sync.
    """
    language_codes = [
        language_code for language_code, _ in settings.LANGUAGES
        if not language_code == settings.LANGUAGE_CODE
    ]

    # We dynamically retrieve the languages from DynamoDB at startup, so check
    # here to make sure we got a full list. We default to a list containing
    # just three languages, so we naively identify a "full list" by simply
    # checking for a list longer than than.
    if len(language_codes) <= 3:
        log("Could not find full list of languages; using default")

    return language_codes


def get_non_english_locale_names():
    """
    Retrieve all locale names (ie "es_MX") for languages we need to process
    in the i18n sync.
    """
    return [
        to_locale(language_code) for language_code
        in get_non_english_language_codes()
    ]

def log(message):
    """
    Generic helper for logging information from the sync process. Message is
    logged to the console mostly for debugging purposes, and is logged to slack
    for actual use.
    """
    print(message) # pylint: disable=superfluous-parens
    try:
        slack_message('slack/message.slack', {
            'message': message
        })
    except TemplateDoesNotExist:
        # This is silly, but when trying to test requests we run into issues
        # because the message template is not loaded in our test environment.
        pass

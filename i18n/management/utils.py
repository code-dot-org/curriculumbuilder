"""
Helper methods for use during the i18n sync process
"""
import django.apps

from django.conf import settings
from django_slack import slack_message

from i18n.models import Internationalizable


def should_sync_model(model):
    """
    whether or not the given Django model is something the i18n sync should
    process. We care about models that:
        - extend the Internationalizable model defined by this module
        - are not proxy models (used by Django Admin for editing)
    """
    is_internationalizable = issubclass(model, Internationalizable)
    is_not_proxy = not model._meta.proxy # pylint: disable=protected-access
    return is_internationalizable and is_not_proxy

def get_models_to_sync():
    """Retrieve all models that should be processed by the i18n sync"""
    return [model for model in django.apps.apps.get_models() if should_sync_model(model)]

def get_non_english_language_codes():
    """
    Retrieve all languages codes (ie "es-mx") for languages we need to process
    in the i18n sync.
    """
    return [
        locale for locale, _ in settings.LANGUAGES
        if not locale == settings.LANGUAGE_CODE
    ]

def log(message):
    """
    Generic helper for logging information from the sync process. Message is
    logged to the console mostly for debugging purposes, and is logged to slack
    for actual use.
    """
    print(message) # pylint: disable=superfluous-parens
    slack_message('slack/message.slack', {
        'message': message
    })

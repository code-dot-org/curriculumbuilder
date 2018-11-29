import re
import warnings

from django.conf import settings
from django.conf.urls import patterns, url
from django.core.urlresolvers import LocaleRegexURLResolver
from django.utils import six
from django.utils.deprecation import RemovedInDjango20Warning

class LocaleRegexURLResolverNoDefaultLanguagePrefix(LocaleRegexURLResolver):
    """
    subclass of LocaleRegexURLResolver which overrides the regex for the default
    language to support both prefix and non-prefix versions
    """
    def __init__(self, *args, **kwargs):
        super(LocaleRegexURLResolverNoDefaultLanguagePrefix, self).__init__(*args, **kwargs)
        self._regex_dict[settings.LANGUAGE_CODE] = re.compile('(^%s/)?' % settings.LANGUAGE_CODE, re.UNICODE)

def i18n_patterns_no_default_language_prefix(prefix, *args):
    """
    based on django.conf.urls.i18n.i18n_patterns, but with a custom
    LocaleRegexURLResolver specifically to avoid prefixing the default language.
    In Django >1.10, this is provided by the prefix_default_language argument
    (see https://docs.djangoproject.com/en/1.10/topics/i18n/translation/#django.conf.urls.i18n.i18n_patterns),
    so if we ever upgrade to that all this can be removed
    """
    if isinstance(prefix, six.string_types):
        warnings.warn(
            "Calling i18n_patterns() with the `prefix` argument and with tuples "
            "instead of django.conf.urls.url() instances is deprecated and "
            "will no longer work in Django 2.0. Use a list of "
            "django.conf.urls.url() instances instead.",
            RemovedInDjango20Warning, stacklevel=2
        )
        pattern_list = patterns(prefix, *args)
    else:
        pattern_list = [prefix] + list(args)
    if not settings.USE_I18N:
        return pattern_list
    return [LocaleRegexURLResolverNoDefaultLanguagePrefix(pattern_list)]

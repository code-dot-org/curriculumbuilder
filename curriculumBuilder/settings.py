from __future__ import absolute_import, unicode_literals

import socket

import os

import urlparse

import dj_database_url

from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

######################
# MEZZANINE SETTINGS #
######################

# The following settings are already defined with default values in
# the ``defaults.py`` module within each of Mezzanine's apps, but are
# common enough to be put here, commented out, for conveniently
# overriding. Please consult the settings documentation for a full list
# of settings Mezzanine implements:
# http://mezzanine.jupo.org/docs/configuration.html#default-settings

# Controls the ordering and grouping of the admin menu.
#
# ADMIN_MENU_ORDER = (
#     ("Content", ("pages.Page", "blog.BlogPost",
#        "generic.ThreadedComment", (_("Media Library"), "fb_browse"),)),
#     ("Site", ("sites.Site", "redirects.Redirect", "conf.Setting")),
#     ("Users", ("auth.User", "auth.Group",)),
# )
ADMIN_MENU_COLLAPSED = False

# A three item sequence, each containing a sequence of template tags
# used to render the admin dashboard.
#
# DASHBOARD_TAGS = (
#     ("blog_tags.quick_blog", "mezzanine_tags.app_list"),
#     ("comment_tags.recent_comments",),
#     ("mezzanine_tags.recent_actions",),
# )

# A sequence of templates used by the ``page_menu`` template tag. Each
# item in the sequence is a three item sequence, containing a unique ID
# for the template, a label for the template, and the template path.
# These templates are then available for selection when editing which
# menus a page should appear in. Note that if a menu template is used
# that doesn't appear in this setting, all pages will appear in it.

PAGE_MENU_TEMPLATES = (
    (1, _("Main Curriculum Listing"), "pages/menus/dropdown.html"),
    (2, _("Unused"), "pages/menus/tree.html"),
    (3, _("Unused"), "pages/menus/footer.html"),
)

# A sequence of fields that will be injected into Mezzanine's (or any
# library's) models. Each item in the sequence is a four item sequence.
# The first two items are the dotted path to the model and its field
# name to be added, and the dotted path to the field class to use for
# the field. The third and fourth items are a sequence of positional
# args and a dictionary of keyword args, to use when creating the
# field instance. When specifying the field class, the path
# ``django.models.db.`` can be omitted for regular Django model fields.
#
# EXTRA_MODEL_FIELDS = (
#     (
#         # Dotted path to field.
#         "mezzanine.blog.models.BlogPost.image",
#         # Dotted path to field class.
#         "somelib.fields.ImageField",
#         # Positional args for field class.
#         (_("Image"),),
#         # Keyword args for field class.
#         {"blank": True, "upload_to": "blog"},
#     ),
#     # Example of adding a field to *all* of Mezzanine's content types:
#     (
#         "mezzanine.pages.models.Page.another_field",
#         "IntegerField", # 'django.db.models.' is implied if path is omitted.
#         (_("Another name"),),
#         {"blank": True, "default": 1},
#     ),
# )

# Setting to turn on featured images for blog posts. Defaults to False.
#
# BLOG_USE_FEATURED_IMAGE = True

# If True, the django-modeltranslation will be added to the
# INSTALLED_APPS setting.

INLINE_EDITING_ENABLED = True

USE_MODELTRANSLATION = False

JQUERY_FILENAME = "jquery-1.12.3.min.js"
JQUERY_UI_FILENAME = "jquery-ui-1.9.1.custom.min.js"

########################
# MAIN DJANGO SETTINGS #
########################

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# If you set this to True, Django will use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en"

# Supported languages
LANGUAGES = (
    ('en', _('English')),
)

# A boolean that turns on/off debug mode. When set to ``True``, stack traces
# are displayed for error pages. Should always be set to ``False`` in
# production. Best set to ``True`` in local_settings.py

SECRET_KEY = os.getenv("DJANGO_SECURITY_KEY", ')_7av^!cy(wfx=k#3*7x+(=j^fzv+ot^1@sh9s9t=8$bu@r(z$')

# SECURITY WARNING: don't run with debug turned on in production!
# adjust to turn off when on Openshift, but allow an environment variable to override on PAAS
DEBUG = os.getenv("debug", "false").lower() == "true"

LOGIN_EXEMPT_URLS = (r'^admin/', r'^robots.txt$', r'^password_reset/', r'^reset/', r'^api/')

# ALLOWED_HOSTS = [os.environ['OPENSHIFT_APP_DNS'], socket.gethostname(), 'testserver', '.rhcloud.com',
#                      '.codecurricula.com']

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*']

ADMINS = [('Josh', 'josh@code.org')]
SERVER_EMAIL = 'root@codecurricula.com'
DEFAULT_FROM_EMAIL = 'josh@code.org'

# LOGIN_REDIRECT_URL = 'https://code.org' # Avoid redirecting randos to our login page
# LOGIN_URL = 'https://code.org' # Avoid redirecting randos to our login page

# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

AUTHENTICATION_BACKENDS = ("mezzanine.core.auth_backends.MezzanineBackend",)

# The numeric mode to set newly-uploaded files to. The value should be
# a mode you'd pass directly to os.chmod.
FILE_UPLOAD_PERMISSIONS = 0o644

WSGI_APPLICATION = 'curriculumBuilder.wsgi.application'

#############
# DATABASES #
#############

DATABASES = {
    "default": dj_database_url.config(default='postgres://localhost/curriculumbuilder', conn_max_age=500),
}

#########
# PATHS #
#########

# Full filesystem path to the project.
PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_APP = os.path.basename(PROJECT_APP_PATH)
PROJECT_ROOT = BASE_DIR = os.path.dirname(PROJECT_APP_PATH)

# Every cache key will get prefixed with this value - here we set it to
# the name of the directory the project is in to try and use something
# project specific.
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_APP

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
# STATIC_URL = "/static/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'wsgi', 'static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

if os.environ.get('REDIS_URL', False):
    redis_url = urlparse.urlparse(os.environ.get('REDIS_URL'))
    CACHES = {
        "default": {
            "BACKEND": "redis_cache.RedisCache",
            "LOCATION": "{0}:{1}".format(redis_url.hostname, redis_url.port),
            "OPTIONS": {
                "PASSWORD": redis_url.password,
                "DB": 0,
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
# MEDIA_URL = STATIC_URL + "media/"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip("/").split("/"))

# Package/module name to import the root urlpatterns from for the project.
ROOT_URLCONF = "%s.urls" % PROJECT_APP

################
# APPLICATIONS #
################

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.admindocs",
    "collectfast",  # Needs to come before staticfiles
    "django.contrib.staticfiles",
    "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    "mezzanine.pages",
    # "mezzanine.blog",
    # "mezzanine.forms",
    # "mezzanine.galleries",
    # "mezzanine.twitter",
    # "mezzanine.accounts",
    "mezzanine.mobile",
    # Third party apps
    "mezzanine_pagedown",
    # "csvimport.app.CSVImportConf",
    "gunicorn",
    "import_export",
    # "data_importer",
    "ajax_select",
    # "wkhtmltopdf",
    "django_medusa",
    "freeze",
    "jackfrost",
    "storages",
    "rest_framework",
    "corsheaders",
    "smuggler",
    "sortedm2m",
    "reversion",
    "reversion_compare",
    "django_slack",
    # Custom apps for Code.org curriculum
    "standards",
    "lessons",
    "curricula",
    "documentation",
    "gong"
)

TEMPLATES = [{u'APP_DIRS': False,
              u'BACKEND': u'django.template.backends.django.DjangoTemplates',
              u'DIRS': (os.path.join(PROJECT_ROOT, "templates"),),
              u'OPTIONS': {
                  u'context_processors': (u'django.contrib.auth.context_processors.auth',
                                          u'django.contrib.messages.context_processors.messages',
                                          'django.core.context_processors.csrf',
                                          u'django.core.context_processors.debug',
                                          u'django.core.context_processors.i18n',
                                          u'django.core.context_processors.static',
                                          u'django.core.context_processors.media',
                                          u'django.core.context_processors.request',
                                          u'django.core.context_processors.tz',
                                          u'mezzanine.conf.context_processors.settings',
                                          u'mezzanine.pages.context_processors.page'),
                  u'loaders': [(u'django.template.loaders.cached.Loader',
                               (u'django.template.loaders.filesystem.Loader',
                                u'django.template.loaders.app_directories.Loader'))]}
              }
             ]

# List of middleware classes to use. Order is important; in the request phase,
# these middleware classes will be applied in the order given, and in the
# response phase the middleware will be applied in reverse order.
MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    "mezzanine.core.middleware.UpdateCacheMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Uncomment if using internationalisation or localisation
    # 'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "mezzanine.core.request.CurrentRequestMiddleware",
    "mezzanine.core.middleware.RedirectFallbackMiddleware",
    "mezzanine.core.middleware.TemplateForDeviceMiddleware",
    "mezzanine.core.middleware.TemplateForHostMiddleware",
    "mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware",
    "mezzanine.core.middleware.SitePermissionMiddleware",
    # Uncomment the following if using any of the SSL settings:
    # "mezzanine.core.middleware.SSLRedirectMiddleware",
    "mezzanine.pages.middleware.PageMiddleware",
    "mezzanine.core.middleware.FetchFromCacheMiddleware",
    "curriculumBuilder.disable_csrf.DisableCSRF",
    # "curriculumBuilder.login_required_middleware.LoginRequiredMiddleware",
)

# Store these package names here as they may change in the future since
# at the moment we are using custom forks of them.
PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"

#########################
# OPTIONAL APPLICATIONS #
#########################

# These will be added to ``INSTALLED_APPS``, only if available.
OPTIONAL_APPS = (
    "debug_toolbar",
    "django_extensions",
    "compressor",
    PACKAGE_NAME_FILEBROWSER,
    PACKAGE_NAME_GRAPPELLI,
)

DEBUG_TOOLBAR_CONFIG = {
'INTERCEPT_REDIRECTS': True,
}

#####################
# PAGEDOWN SETTINGS #
#####################

CODEMIRROR_MODE = 'markdown'
CODEMIRROR_CONFIG = {
    'lineNumbers': False,
    'lineWrapping': True,
    'autoRefresh': True,
    'autoCloseBrackets': True,
    'matchBrackets': True,
}
CODEMIRROR_ADDON_JS = (
    "display/autorefresh",
    "edit/closebrackets",
    "edit/matchbrackets",
    "edit/closetag",
    "edit/continuelist",
    "display/panel",
    "display/buttons",
    "attach/inline-attachment",
    "attach/codemirror-4.inline-attachment"
)
CODEMIRROR_ADDON_CSS = {
    "display/buttons"
}

# CODEMIRROR_JS_VAR_FORMAT = "%s_editor"

# RICHTEXT_WIDGET_CLASS = 'mezzanine_pagedown.widgets.PageDownWidget'
RICHTEXT_WIDGET_CLASS = 'codemirror.CodeMirrorTextarea'
RICHTEXT_FILTER = 'mezzanine_pagedown.filters.custom'
RICHTEXT_FILTERS = (RICHTEXT_FILTER,)
RICHTEXT_ALLOWED_TAGS = ('a', 'abbr', 'acronym', 'address', 'area', 'article', 'aside', 'b', 'bdo', 'big',
                         'blockquote', 'br', 'button', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'dd',
                         'del', 'dfn', 'dir', 'div', 'display', 'dl', 'dt', 'em', 'fieldset', 'figure', 'font', 'footer', 'form',
                         'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'label',
                         'legend', 'li', 'map', 'men', 'nav', 'object', 'ol', 'optgroup', 'option', 'p', 'pre', 'q', 's', 'samp',
                         'section', 'select', 'small', 'span', 'strike', 'strong', 'sub', 'sup', 'table', 'tbody', 'td',
                         'textarea', 'tfoot', 'th', 'thead', 'tr', 'tt', '', 'ul', 'var', 'wbr', 'summary', 'details')
RICHTEXT_ALLOWED_STYLES = ('margin-top', 'margin-bottom', 'margin-left', 'margin-right', 'float', 'vertical-align',
                           'border', 'margin', 'width', 'height', 'max-width', 'padding', 'margin', 'style',
                           'data-pdf-link', 'data-lightbox', 'data-title', 'color', 'background', 'background-color')
RICHTEXT_ALLOWED_ATTRIBUTES = (
    'abbr', 'accept', 'accept-charset', 'accesskey', 'action', 'align', 'alt', 'axis', 'border',
    'cellpadding', 'cellspacing', 'char', 'charoff', 'charset', 'checked', 'cite', 'class',
    'clear', 'cols', 'colspan', 'color', 'compact', 'coords', 'data', 'datetime', 'dir', 'disabled',
    'enctype', 'for', 'frame', 'headers', 'height', 'href', 'hreflang', 'hspace', 'id',
    'ismap', 'label', 'lang', 'longdesc', 'maxlength', 'media', 'method', 'multiple', 'name',
    'nohref', 'noshade', 'nowrap', 'open', 'prompt', 'readonly', 'rel', 'rev', 'role','rows', 'rowspan',
    'rules', 'scope', 'selected', 'shape', 'size', 'span', 'src', 'start', 'style', 'summary',
    'tabindex', 'target', 'title', 'type', 'usemap', 'valign', 'value', 'vspace', 'width',
    'xml:lang', 'data-pdf-link', 'data-lightbox', 'data-title', 'data-start', 'data-end', 'aria-expanded')
PAGEDOWN_MARKDOWN_EXTENSIONS = (
    'curriculumBuilder.doclinks',
    'extra', 'codehilite', 'toc', 'curriculumBuilder.newtab', 'curriculumBuilder.absolute_images',
    # 'curriculumBuilder.resourcelinks', 'curriculumBuilder.highlightblocks', 'smarty',
    'curriculumBuilder.resourcelinks', 'curriculumBuilder.mdlightbox',
    'curriculumBuilder.vocablinks', 'curriculumBuilder.tips', 'curriculumBuilder.tiplinks',
    'curriculumBuilder.iconfonts', 'curriculumBuilder.codestudio', 'curriculumBuilder.divclass')
RICHTEXT_FILTER_LEVEL = 3
PAGEDOWN_SERVER_SIDE_PREVIEW = False

#####################
# SMUGGLER SETTINGS #
#####################

SMUGGLER_EXCLUDE_LIST = ['sites.site']

#######################
# AJAXSELECT SETTINGS #
#######################

AJAX_LOOKUP_CHANNELS = {
    'resources': ('curriculumBuilder.lookups', 'ResourceLookup'),
    'vocab': {'model': 'lessons.vocab', 'search_field': 'word'},
    'standards': {'model': 'standards.standard', 'search_field': 'shortcode'},
}

########################
# WKHTMLTOPDF SETTINGS #
########################

WKHTMLTOPDF_BIN = os.environ.get('WKHTMLTOPDF_BIN')

WKHTMLTOPDF_CMD_OPTIONS = {
    'page-size': 'Letter',
    'print-media-type': '',
    'javascript-delay': 10000,
    'debug-javascript': '',
    'no-stop-slow-scripts': '',
    'load-error-handling': 'ignore',
    'load-media-error-handling': 'ignore'
}

############################
# PHANTOMJS CLOUD SETTINGS #
############################

PHANTOMJS_KEY = os.environ.get('PHANTOMJS_KEY')

###################
# S3 STATIC FILES #
###################

AWS_QUERYSTRING_AUTH = False
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'cdo-curriculum'
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_CUSTOM_DOMAIN = 'curriculum.code.org'
AWS_PRELOAD_METADATA = True  # helps collectstatic do updates
AWS_HEADERS = {
 'Cache-Control': 'max-age=0',
}

AWS_BASE_URL = 'http://cdo-curriculum.s3-website-us-east-1.amazonaws.com'

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'curriculumBuilder.s3utils.StaticRootS3BotoStorage'
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'curriculumBuilder.s3utils.MediaRootS3BotoStorage'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)

# STATIC_URL = 'https://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/static/'
# ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'
# MEDIA_URL = 'https://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/media/'

###################
# MEDUSA SETTINGS #
###################
MEDUSA_RENDERER_CLASS = "django_medusa.renderers.S3StaticSiteRenderer"
MEDUSA_MULTITHREAD = False
AWS_ACCESS_KEY = AWS_ACCESS_KEY_ID
MEDUSA_AWS_STORAGE_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME
# PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# MEDUSA_DEPLOY_DIR = os.path.join(
#  PROJECT_DIR, '..', "_output"
# )

###################
# FREEZE SETTINGS #
###################

FREEZE_INCLUDE_STATIC = False

######################
# JACKFROST SETTINGS #
######################
JACKFROST_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
JACKFROST_RENDERERS = (
    'curricula.jackfrost_renderers.CurriculumRenderer',
    'curricula.jackfrost_renderers.UnitRenderer',
    'curricula.jackfrost_renderers.LessonRenderer',
    'curricula.jackfrost_renderers.IDERenderer',
    'curricula.jackfrost_renderers.BlockRenderer',
    'curricula.jackfrost_renderers.UnitPDFRenderer',
)

AUTO_PUBLISH = False  # os.getenv("AUTO_PUBLISH", "False").lower() == "true"

ENABLE_PUBLISH = True

######################
# REVERSION SETTINGS #
######################

CHANGELOG_USER = "changelog"
FEEDBACK_USER = "feedback"
RESOLVED_USER = "resolved"
ADD_REVERSION_ADMIN = True

#################
# CORS SETTINGS #
#################

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = ('GET',
                      'POST',
                      'PUT',
                      'DELETE',
                      'OPTIONS'
                      )

###################
# DISQUS SETTINGS #
###################

COMMENTS_DISQUS_API_PUBLIC_KEY = 'wfS3VtMuylVdTyih6dAvcbztv0KzWYl8VplU8la3EgK4BCpyVSK09ieW6rMFKJ2t'

COMMENTS_DISQUS_API_SECRET_KEY = os.environ.get('DISQUS_API_SECRET_KEY')

COMMENTS_DISQUS_SHORTNAME = 'CurriculumBuilder'

##################
# EMAIL SETTINGS #
##################

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

################
# CELERY STUFF #
################

BROKER_URL = 'redis://:%s@%s:%s/0' % (os.environ.get('REDISCLOUD_PASSWORD'),
                                      os.environ.get('REDISCLOUD_HOSTNAME'),
                                      os.environ.get('REDISCLOUD_PORT'))
CELERY_RESULT_BACKEND = BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Los_Angeles'

#####################
# COMPRESS SETTINGS #
#####################

COMPRESS_STORAGE = 'curriculumBuilder.s3utils.StaticRootS3BotoStorage'
COMPRESS_URL = STATIC_URL

##################
# SLACK SETTINGS #
##################

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', "#curriculumbuilder")
SLACK_USERNAME = os.environ.get('SLACK_USER', 'curricbot')
SLACK_ENDPOINT_URL = 'https://hooks.slack.com/services/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'

###########
# LOGGING #
###########

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'DEBUG',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': False,
        },
        'slack_admins': {
            'level': 'DEBUG',
            'class': 'django_slack.log.SlackExceptionHandler',
            'include_html': False,
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins', 'slack_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'jackfrost': {
            'handlers': ['console', 'mail_admins', 'slack_admins'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True
        },
        'lessons': {
            'handlers': ['console', 'slack_admins'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': True
        },
        'curricula': {
            'handlers': ['console', 'slack_admins'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': True
        },
        'pdfkit': {
            'handlers': ['console', 'mail_admins', 'slack_admins'],
            'level': 'DEBUG',
            'propagate': True
        },
        'PyPDF2': {
            'handlers': ['console', 'mail_admins', 'slack_admins'],
            'level': 'DEBUG',
            'propagate': True
        }
    },
}

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
try:
    from .local_settings import *
except ImportError as e:
    if "local_settings" not in str(e):
        raise e

####################
# DYNAMIC SETTINGS #
####################

# set_dynamic_settings() will rewrite globals based on what has been
# defined so far, in order to provide some better defaults where
# applicable. We also allow this settings module to be imported
# without Mezzanine installed, as the case may be when using the
# fabfile, where setting the dynamic settings below isn't strictly
# required.
try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())

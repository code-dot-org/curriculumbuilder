from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from ajax_select import urls as ajax_select_urls

from rest_framework import serializers, viewsets, routers

from mezzanine.core.views import direct_to_template
from mezzanine.conf import settings
from mezzanine.core import views as core_views
import mezzanine_pagedown.urls
import freeze.urls

from curricula import views
from standards.views import *
from gong import views as gong_views

admin.autodiscover()

# Add the urlpatterns for any custom Django applications here.
# You can also change the ``home`` view to add your own functionality
# to the project's homepage.

urlpatterns = i18n_patterns("",
    # Change the admin prefix here to use an alternate URL for the
    # admin interface, which would be marginally more secure.
    (r'^admin/lookups/', include(ajax_select_urls)),
    (r'^admin/', include('smuggler.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.USE_MODELTRANSLATION:
    urlpatterns += patterns('',
        url('^i18n/$', 'django.views.i18n.set_language', name='set_language'),
    )

urlpatterns += patterns('',
    # We don't want to presume how your homepage works, so here are a
    # few patterns you can use to set it up.

    # HOMEPAGE AS STATIC TEMPLATE
    # ---------------------------
    # This pattern simply loads the index.html template. It isn't
    # commented out like the others, so it's the default. You only need
    # one homepage pattern, so if you use a different one, comment this
    # one out.

    # url("^$", direct_to_template, {"template": "curricula/index.html"}, name="home"),

    # HOMEPAGE AS AN EDITABLE PAGE IN THE PAGE TREE
    # ---------------------------------------------
    # This pattern gives us a normal ``Page`` object, so that your
    # homepage can be managed via the page tree in the admin. If you
    # use this pattern, you'll need to create a page in the page tree,
    # and specify its URL (in the Meta Data section) as "/", which
    # is the value used below in the ``{"slug": "/"}`` part.
    # Also note that the normal rule of adding a custom
    # template per page with the template name using the page's slug
    # doesn't apply here, since we can't have a template called
    # "/.html" - so for this case, the template "pages/index.html"
    # should be used if you want to customize the homepage's template.

    # url("^$", "mezzanine.pages.views.page", {"slug": "/"}, name="home"),
    url(r'^$', views.index, name='home'),

    # HOMEPAGE FOR A BLOG-ONLY SITE
    # -----------------------------
    # This pattern points the homepage to the blog post listing page,
    # and is useful for sites that are primarily blogs. If you use this
    # pattern, you'll also need to set BLOG_SLUG = "" in your
    # ``settings.py`` module, and delete the blog page object from the
    # page tree in the admin if it was installed.

    # url("^$", "mezzanine.blog.views.blog_post_list", name="home"),

    url("^edit/$", views.reversion_edit, name="edit"),
    url("^search/$", core_views.search, name="search"),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    url("^None/$", views.index),  # Dealing with JackFrost bug
    url(r'^documentation/', include('documentation.urls', namespace="documentation")),
    url(r'^standards/', include('standards.urls', namespace="standards")),
    url(r'^', include('curricula.urls', namespace="curriculum")),

    # MEZZANINE'S URLS
    # ----------------
    # ADD YOUR OWN URLPATTERNS *ABOVE* THE LINE BELOW.
    # ``mezzanine.urls`` INCLUDES A *CATCH ALL* PATTERN
    # FOR PAGES, SO URLPATTERNS ADDED BELOW ``mezzanine.urls``
    # WILL NEVER BE MATCHED!

    # If you'd like more granular control over the patterns in
    # ``mezzanine.urls``, go right ahead and take the parts you want
    # from it, and use them directly below instead of using
    # ``mezzanine.urls``.

    # Curriculum URLs
    url(r'^api/v1/$', views.api_root),
    url(r'^api/v1/proxy/(?P<api_type>[-\w]+)/(?P<api_args>.+)', views.proxy_api),
    url(r'^api/v1/gong/$', gong_views.gong),
    url(r'^api/v1/feedback/$', views.feedback),
    url(r'^api/v1/arduino/(?P<command>[0-9a-zA-Z/]+)/$', views.arduino),
    url(r'^api/v1/gong/get/$', gong_views.get_gongs),
    url(r'^api/v1/curriculum/$', views.curriculum_list, name="curriculum_list"),
    url(r'^api/v1/curriculum/(?P<curriculum_slug>[-\w]+)/standards/$', standard_list, name="standard_list"),
    # url(r'^api/v1/curriculum/(?P<curriculum_slug>[-\w]+)/standards/(?P<framework_slug>[-\w]+)/$', standard_list, name="standard_list"),
    url(r'^api/v1/curriculum/(?P<curriculum_slug>[-\w]+)/standards/(?P<framework_slug>[-\w]+)/$', nested_category_list, name="nested_category_list"),
    url(r'^api/v1/curriculum/(?P<curriculum_slug>[-\w]+)/standards/(?P<framework_slug>[-\w]+)/standards/$', nested_standard_list, name="nested_standard_list"),
    url(r'^api/v1/curriculum/(?P<slug>[-\w]+)/$', views.curriculum_element, name="curriculum_element"),
    url(r'^api/v1/curriculum/(?P<slug>[-\w]+)/units/$', views.unit_list, name="unit_list"),
    url(r'^api/v1/curriculum/(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/$', views.unit_element, name="unit_element"),
    url(r'^api/v1/curriculum/(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/$', views.lesson_element, name="lesson_element"),
    #url(r'^api/v1/annotations$', AnnotationList.as_view()),
    #url(r'^api/v1/annotations/(?P<pk>[0-9]+)$', AnnotationMember.as_view()),
    url(r'^api/v1/comments/', include('curricula.api', namespace="api")),

    url(r'^freeze/', include(freeze.urls)),
    url(r'^pagedown/', include(mezzanine_pagedown.urls)),
    ("^", include("mezzanine.urls")),
    # MOUNTING MEZZANINE UNDER A PREFIX
    # ---------------------------------
    # You can also mount all of Mezzanine's urlpatterns under a
    # URL prefix if desired. When doing this, you need to define the
    # ``SITE_PREFIX`` setting, which will contain the prefix. Eg:
    # SITE_PREFIX = "my/site/prefix"
    # For convenience, and to avoid repeating the prefix, use the
    # commented out pattern below (commenting out the one above of course)
    # which will make use of the ``SITE_PREFIX`` setting. Make sure to
    # add the import ``from django.conf import settings`` to the top
    # of this file as well.
    # Note that for any of the various homepage patterns above, you'll
    # need to use the ``SITE_PREFIX`` setting as well.

    #("^%s/" % settings.SITE_PREFIX, include("mezzanine.urls"))


)


if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]

# Adds ``STATIC_URL`` to the context of error pages, so that error
# pages can use JS, CSS and images.
handler404 = "mezzanine.core.views.page_not_found"
handler500 = "mezzanine.core.views.server_error"

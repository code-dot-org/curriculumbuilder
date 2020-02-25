from __future__ import absolute_import
from django.conf.urls import patterns, url
from .views import ResourceCreateView

urlpatterns = patterns(
  'lessons.views',
  url(r'^resource/create/$', ResourceCreateView.as_view(), name="resource_create"),
)
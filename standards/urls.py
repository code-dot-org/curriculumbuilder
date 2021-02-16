from django.conf.urls import patterns, url

from standards import views

urlpatterns = patterns('standards.views',
                       url(r'^$', views.index, name='index'),
                       url(r'^curriculum/(?P<slug>[-\w]+)/$', views.by_curriculum, name='by_curriculum'),
                       url(r'^curriculum/(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/$', views.by_unit, name='by_unit'),
                       url(r'^framework/(?P<slug>[-\w]+)/$', views.by_framework, name='by_framework'),
                       url(r'^framework/(?P<slug>[-\w]+).csv$', views.by_framework_csv, name='by_framework_csv'),
                       url(r'^framework/(?P<slug>[-\w]+)/(?P<shortcode>[-\S]+)/$', views.single_standard, name='single_standard'),
                       # url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/$', views.unit_view, name='unit_view'),
                       # url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)$', views.lesson_view, name='lesson_view'),
                       )

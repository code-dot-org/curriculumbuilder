from django.conf.urls import patterns, url

from curricula import views
from standards import views as standards_views

urlpatterns = patterns('curricula.views',
                       url(r'^$', views.index, name='index'),
                       url(r'^(?P<slug>[-\w]+)/$', views.curriculum_view, name='curriculum_view'),
                       url(r'^(?P<slug>[-\w]+)/pdf$', views.curriculum_pdf, name='curriculum_pdf'),
                       url(r'^(?P<slug>[-\w]+)/resources/$', views.curriculum_resources, name='curriculum_resources'),
                       url(r'^(?P<slug>[-\w]+)/standards/$', standards_views.by_curriculum, name='by_curriculum'),
                       url(r'^(?P<slug>[-\w]+)/standards/(?P<unit_slug>[-\w]+)/$', standards_views.by_unit, name='by_unit'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/$', views.unit_view, name='unit_view'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/pdf$', views.unit_pdf, name='unit_pdf'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/standards/$', standards_views.by_unit, name='by_unit_2'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/ch(?P<chapter_num>\d+)/$', views.chapter_view, name='chapter_view'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/$', views.lesson_view, name='lesson_view'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/pdf$', views.lesson_pdf, name='lesson_pdf'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/md$', views.lesson_markdown, name='lesson_markdown'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/optional/(?P<optional_num>\d+)/$', views.lesson_view, name='lesson_optional'),
                       )
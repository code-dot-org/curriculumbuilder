from django.conf.urls import patterns, url

from curricula import views
from standards import views as standards_views
from documentation import views as documentation_views

urlpatterns = patterns('curricula.views',
                       url(r'^$', views.index, name='home'),
                       url(r'^page_history/(?P<page_id>\d+)/$', views.page_history, name='page_history'),
                       url(r'^publish/$', views.publish, name='publish'),
                       url(r'^upload/$', views.image_upload, name='image_upload'),
                       url(r'^get_stage_details/$', views.get_stage_details, name='get_stage_details'),
                       url(r'^metadata/(?P<stage>[-\w]+).json$', views.stage_element, name="stage_element"),

                       # Documentation URLS

                       url(r'^(?P<slug>[-\w]+lab)/$',
                           documentation_views.ide_view, name='ide_view'),
                       url(r'^(?P<ide_slug>[-\w]+lab)/(?P<slug>[-\w.]+)/$',
                           documentation_views.block_view, name='block_view'),
                       url(r'^(?P<ide_slug>[-\w]+lab)/(?P<slug>[-\w.]+)/embed/$',
                           documentation_views.embed_view, name='embed_view'),

                       # Curriculum URLS
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/$', views.curriculum_view, name='curriculum_view'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/pdf$', views.curriculum_pdf, name='curriculum_pdf'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/code/$', views.curriculum_code, name='curriculum_code'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/vocab/$', views.curriculum_vocab, name='curriculum_vocab'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/resources/$',
                           views.curriculum_resources, name='curriculum_resources'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/standards/$',
                           standards_views.by_curriculum, name='by_curriculum'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/standards/(?P<unit_slug>[a-zA-Z]+)/$',
                           standards_views.by_unit, name='by_unit'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/$',
                           views.unit_view, name='unit_view'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/compiled/$',
                           views.unit_compiled, name='unit_compiled'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+).json$',
                           views.unit_element, name="unit_element"),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+).pdf$',
                           views.unit_pdf, name='unit_pdf'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/glance/$',
                           views.unit_at_a_glance, name='unit_at_a_glance'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/code/$',
                           views.unit_code, name='unit_code'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/vocab/$',
                           views.unit_vocab, name='unit_vocab'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/resources/$',
                           views.unit_resources, name='unit_resources'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)_resources.pdf$',
                           views.unit_resources_pdf, name='unit_resources_pdf'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/standards/$',
                           standards_views.by_unit, name='by_unit_2'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/ch(?P<chapter_num>\d+)/$',
                           views.chapter_view, name='chapter_view'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/(?P<lesson_num>\d+)/$',
                           views.lesson_view, name='lesson_view'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/(?P<lesson_num>\d+)/pdf/$',
                           views.lesson_pdf, name='lesson_pdf'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/(?P<lesson_num>\d+)/md/$',
                           views.lesson_markdown, name='lesson_markdown'),
                       url(r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/(?P<lesson_num>\d+)/overview/$',
                           views.lesson_overview, name='lesson_overview'),
                       url(
                           r'^(?P<slug>[0-9a-zA-Z]+)/(?P<unit_slug>[0-9a-zA-Z]+)/(?P<lesson_num>\d+)/optional/(?P<optional_num>\d+)/$',
                           views.lesson_view, name='lesson_optional'),

                       )

from django.conf.urls import patterns, url

from curricula import views
from standards import views as standards_views
from documentation import views as documentation_views

urlpatterns = patterns('curricula.views',
                       url(r'^$', views.index, name='home'),

                       # Ajax endpoints
                       # url(r'^page_history/(?P<page_id>\d+)/$', views.page_history, name='page_history'),
                       # url(r'^test_view/(?P<pk>\d+)/$', views.CompareHistoryView.as_view() ),
                       url(r'^page_history/(?P<pk>\d+)/$', views.CompareHistoryView.as_view()),
                       url(r'^publish/$', views.publish, name='publish'),
                       url(r'^clone/$', views.clone, name='clone'),
                       url(r'^upload/$', views.image_upload, name='image_upload'),
                       url(r'^get_stage_details/$', views.get_stage_details, name='get_stage_details'),
                       url(r'^resolve_feedback/$', views.resolve_feedback, name='resolve_feedback'),

                       # JSON Metadata
                       url(r'^metadata/(?P<stage>[-\w]+).json$', views.stage_element, name="stage_element"),
                       url(r'^metadata/course/(?P<slug>[-\w]+).json$', views.curriculum_element, name="curriculum_element"),

                       # Curriculum URLs
                       url(r'^(?P<slug>[-\w]+)/$', views.curriculum_view, name='curriculum_view'),
                       url(r'^(?P<slug>[-\w]+).json$', views.onenote_export, name="onenote_export"),
                       url(r'^(?P<slug>[-\w]+)/pdf$', views.curriculum_pdf, name='curriculum_pdf'),
                       url(r'^(?P<slug>[-\w]+)/code/$', views.curriculum_code, name='curriculum_code'),
                       url(r'^(?P<slug>[-\w]+)/vocab/$', views.curriculum_vocab, name='curriculum_vocab'),
                       url(r'^(?P<slug>[-\w]+)/resources/$',
                           views.curriculum_resources, name='curriculum_resources'),
                       url(r'^(?P<slug>[-\w]+)/objectives/$',
                           views.curriculum_objectives, name='curriculum_objectives'),
                       url(r'^(?P<slug>[-\w]+)/standards/$',
                           standards_views.by_curriculum, name='by_curriculum'),
                       url(r'^(?P<slug>[-\w]+)/standards.csv$',
                           standards_views.by_curriculum_csv, name='by_curriculum_csv'),
                       url(r'^(?P<slug>[-\w]+)/standards/(?P<unit_slug>[a-zA-Z]+)/$',
                           standards_views.by_unit, name='by_unit'),

                       # Unit URLs
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/$',
                           views.unit_view, name='unit_view'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/compiled/$',
                           views.unit_compiled, name='unit_compiled'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+).json$',
                           views.unit_element, name="unit_element"),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)_resources.pdf$',
                           views.unit_resources_pdf, name='unit_resources_pdf'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+).pdf$',
                           views.unit_pdf, name='unit_pdf'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/glance/$',
                           views.unit_at_a_glance, name='unit_at_a_glance'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/code/$',
                           views.unit_code, name='unit_code'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/vocab/$',
                           views.unit_vocab, name='unit_vocab'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/resources/$',
                           views.unit_resources, name='unit_resources'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/objectives/$',
                           views.unit_objectives, name='unit_objectives'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/standards/$',
                           standards_views.by_unit, name='by_unit_2'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/standards.csv$',
                           standards_views.by_unit_csv, name='by_unit_csv'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/unit_feedback/$',
                           views.unit_feedback, name='unit_feedback'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/ch(?P<chapter_num>\d+)/$',
                           views.chapter_view, name='chapter_view'),

                       # Lesson URLs
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/$',
                           views.lesson_view, name='lesson_view'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/pdf/$',
                           views.lesson_pdf, name='lesson_pdf'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/md/$',
                           views.lesson_markdown, name='lesson_markdown'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/overview/$',
                           views.lesson_overview, name='lesson_overview'),

                       # Option Lessons (I hates them)
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/optional/(?P<optional_num>\d+)/$',
                           views.lesson_view, name='lesson_optional'),
                       url(r'^(?P<slug>[-\w]+)/(?P<unit_slug>[-\w]+)/(?P<lesson_num>\d+)/optional/(?P<optional_num>\d+)/overview/$',
                           views.lesson_view, name='lesson_overview'),

                       # Documentation URLS
                       url(r'^(?P<slug>[-\w]+lab)/$',
                           documentation_views.ide_view, name='ide_view'),
                       url(r'^(?P<ide_slug>[-\w]+lab)/(?P<slug>[-\w.]+)/$',
                           documentation_views.block_view, name='block_view'),
                       url(r'^(?P<ide_slug>[-\w]+lab)/(?P<slug>[-\w.]+)/embed/$',
                           documentation_views.embed_view, name='embed_view'),
                       url(r'^(?P<curric_slug>[-\w]+)/(?P<slug>[-\w.]+)/$',
                           documentation_views.page_view, name='page_view'),
                       )

from django.conf.urls import patterns, url

from documentation import views

urlpatterns = patterns('curricula.views',
                        #url(r'^$', views.index, name='home'),
                        url(r'^(?P<slug>[-\w]+)/$', views.ide_view, name='ide_view'),
                        url(r'^(?P<ide_slug>[-\w]+)/(?P<slug>[-\w.]+)/$', views.block_view, name='block_view'),
                        url(r'^(?P<ide_slug>[-\w]+)/(?P<slug>[-\w.]+)/embed/$', views.embed_view, name='embed_view'),
                       )
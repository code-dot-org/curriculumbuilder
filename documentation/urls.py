from django.conf.urls import patterns, url

from documentation import views

urlpatterns = patterns('curricula.views',
                        #url(r'^$', views.index, name='home'),
                        url(r'^(?P<slug>[0-9a-zA-Z]+)/$', views.ide_view, name='ide_view'),
                        url(r'^(?P<ide_slug>[0-9a-zA-Z]+)/(?P<slug>[0-9a-zA-Z]+)/$', views.block_view, name='block_view'),
                       )
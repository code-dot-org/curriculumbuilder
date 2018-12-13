from django.conf.urls import url
from multiurl import multiurl

from documentation import views

urlpatterns = [
    multiurl(
        url(r'^(?P<slug>.*)/$', views.map_view, name="map_view"),
        url(r'^(?P<slug>[-\w]+)/$', views.ide_view, name='ide_view'),
        url(r'^(?P<ide_slug>[-\w]+)/(?P<slug>[-\w.]+)/$', views.block_view, name='block_view'),
        url(r'^(?P<ide_slug>[-\w]+)/(?P<slug>[-\w.]+)/embed/$', views.embed_view, name='embed_view'),
    )
]

from django.conf.urls import url
from multiurl import multiurl

from documentation import views

urlpatterns = [
    multiurl(
        url(r'^$', views.index, name='index'),
        url(r'^(?P<slug>.*)/$', views.map_view, name="map_view"),

        # Assumes that all IDEs with docs end in lab to avoid routing conflicts with curriculum routes
        url(r'^(?P<slug>[-\w]+lab)/$', views.ide_view, name='ide_view'),
        url(r'^(?P<ide_slug>[-\w]+lab)/(?P<slug>[-\w.]+)/$', views.block_view, name='block_view'),
        url(r'^(?P<ide_slug>[-\w]+lab)/(?P<slug>[-\w.]+)/embed/$', views.embed_view, name='embed_view'),
    )
]

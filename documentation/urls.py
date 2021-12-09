from django.conf.urls import patterns,url
from multiurl import multiurl

from documentation import views

urlpatterns = [
    multiurl(
        url(r'^$', views.index, name='index'),
        
        # Export this map for import into code studio
        url(r'^export/(?P<slug>.*).json$', views.map_export, name="map_export"),
        
        # Export code docs for import into code studio
        url(r'^export/block/(?P<ide_slug>[-\w]+lab)/(?P<block_slug>[-\w.]+).json$', views.block_export, name="block_export"),

        url(r'^(?P<slug>.*)/$', views.map_view, name="map_view"),

        # Assumes that all IDEs with docs end in lab to avoid routing conflicts with curriculum routes
        url(r'^(?P<slug>[-\w]+lab)/$', views.ide_view, name='ide_view'),
        url(r'^(?P<ide_slug>[-\w]+lab)/(?P<slug>[-\w.]+)/$', views.block_view, name='block_view'),
        url(r'^(?P<ide_slug>[-\w]+lab)/(?P<slug>[-\w.]+)/embed/$', views.embed_view, name='embed_view'),
    )
]

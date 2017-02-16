from django.conf.urls import url
from multiurl import multiurl

from documentation import views

urlpatterns = [
    multiurl(
        # url(r'^$', views.index, name='home'),
        url(r'^(?P<slug>[-\w]+)/$', views.ide_view, name='ide_view'),
        url(r'^(?P<ide_slug>[-\w]+)/(?P<slug>[-\w.]+)/$', views.block_view, name='block_view'),
        url(r'^(?P<ide_slug>[-\w]+)/(?P<slug>[-\w.]+)/embed/$', views.embed_view, name='embed_view'),
        url(r'^(?P<curric_slug>[-\w]+)/(?P<slug>[-\w.]+)/$', views.page_view, name='page_view'),
    )
]

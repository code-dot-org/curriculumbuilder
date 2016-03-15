from django.conf.urls import patterns, url

from rest_framework import serializers, viewsets, routers

from curricula import views

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'annotations', views.AnnotationViewSet)


urlpatterns = patterns("",
    url(r"^search/$", views.AnnotationSearchView.as_view(), name="annotation-search"),
    #url(r"^annotations/$", views.AnnotationListCreateView.as_view(), name="annotation-list"),
    #url(r"^annotations/(?P<pk>[-\w]+)/$", views.AnnotationReadUpdateDeleteView.as_view(),name="annotation-detail"),
)

urlpatterns+= router.urls
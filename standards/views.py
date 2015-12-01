from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, render_to_response

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from standards.serializers import *

from standards.models import *
from curricula.models import Curriculum, Unit
from lessons.models import Lesson


def index(request):
  frameworks = Framework.objects.all()
  curricula = Curriculum.objects.all()
  return render(request, 'standards/index.html', {'frameworks': frameworks, 'curricula': curricula})

def by_framework(request, slug, curriculum_slug = None):
  framework = get_object_or_404(Framework, slug = slug)
  top_categories = Category.objects.filter(framework=framework, parent__isnull=True)\
    .prefetch_related('children__standard_set__lesson_set', 'standard_set__lesson_set')
  return render(request, 'standards/framework.html', {'framework': framework, 'top_categories': top_categories})

def by_curriculum(request, slug):
  curriculum = get_object_or_404(Curriculum, slug = slug)
  #curriculum = get_object_or_404(Curriculum.objects.prefetch_related('unit_set__unitlesson_set__lesson__standards'), slug = slug)
  #units = Unit.objects.filter(curriculum = curriculum).prefetch_related('unitlesson_set__lesson__standards')
  return render(request, 'standards/curriculum.html', {'curriculum': curriculum})

def single_standard(request, slug, shortcode):
  #standard = get_object_or_404(Standard.objects.prefetch_related('lesson_set__unitlesson_set__unit__curriculum'), framework__slug=slug, shortcode=shortcode)
  standard = get_object_or_404(Standard, framework__slug=slug, shortcode=shortcode)
  return render(request, 'standards/standard.html', {'standard': standard})

@api_view(['GET',])
def standard_element(request, slug, shortcode, format=None):
  #standard = get_object_or_404(Standard.objects.prefetch_related('lesson_set__unitlesson_set__unit__curriculum'), framework__slug=slug, shortcode=shortcode)
  standard = get_object_or_404(Standard, framework__slug=slug, shortcode=shortcode)

  serializer = StandardSerializer(standard)
  return Response(serializer.data)

@api_view(['GET',])
def standard_list(request, curriculum_slug, framework_slug=None):

  curriculum = get_object_or_404(Curriculum, slug=curriculum_slug)

  if framework_slug:
    standards = Standard.objects.filter(framework__slug=framework_slug)
  else:
    standards = Standard.objects.all()

  serializer = StandardSerializer(standards, context={'curriculum': curriculum}, many=True)
  return Response(serializer.data)

@api_view(['GET',])
def nested_standard_list(request, curriculum_slug, framework_slug=None):

  curriculum = get_object_or_404(Curriculum, slug=curriculum_slug)

  if framework_slug:
    categories = Category.objects.filter(parent__isnull=True, framework__slug=framework_slug)
    # categories = Category.objects.filter(framework__slug=framework_slug)
  else:
    categories = Category.objects.filter(parent__isnull=True)

  serializer = NestedCategorySerializer(categories, context={'curriculum': curriculum}, many=True)
  return Response(serializer.data)


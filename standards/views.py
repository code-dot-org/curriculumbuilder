from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, render_to_response

from standards.models import *
from curricula.models import Curriculum, Unit
from lessons.models import Lesson


def index(request):
  frameworks = Framework.objects.all()
  curricula = Curriculum.objects.all()
  return render(request, 'standards/index.html', {'frameworks': frameworks, 'curricula': curricula})

def by_framework(request, slug):
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
  standard = get_object_or_404(Standard.objects.prefetch_related('lesson_set__unitlesson_set__unit__curriculum'), framework__slug=slug, shortcode=shortcode)
  return render(request, 'standards/standard.html', {'standard': standard})

'''
def unit_view(request, slug, unit_slug):
  curriculum = get_object_or_404(Curriculum, slug = slug)
  unit = get_object_or_404(Unit, curriculum = curriculum, slug = unit_slug)

  return render(request, 'curricula/unit.html', {'curriculum': curriculum, 'unit': unit})

def lesson_view(request, slug, unit_slug, lesson_num):
  curriculum = get_object_or_404(Curriculum, slug = slug)
  unit = get_object_or_404(Unit, curriculum = curriculum, slug = unit_slug)
  lesson = get_object_or_404(Lesson.objects.prefetch_related('standards__framework', 'anchor_standards__framework',
                                                             'vocab', 'resources', 'activity_set'),
                             unitlesson__unit = unit, _order = int(lesson_num) - 1)
  page = Page.objects.get(pk = lesson.pk)
  if curriculum.slug == 'csp':
    return render(request, 'curricula/csplesson.html', {'curriculum': curriculum, 'unit': unit, 'lesson': lesson})
  else:
    return render(request, 'curricula/lesson.html', {'curriculum': curriculum, 'unit': unit, 'lesson': lesson})
    '''
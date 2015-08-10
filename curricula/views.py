from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, render_to_response

from curricula.models import *

def index(request):
  curricula = Curriculum.objects.all()
  return render(request, 'curricula/index.html', {'curricula': curricula})

def curriculum_view(request, slug):
  curriculum = get_object_or_404(Curriculum, slug = slug)
  return render(request, 'curricula/curriculum.html', {'curriculum': curriculum})

def unit_view(request, slug, unit_slug):
  curriculum = get_object_or_404(Curriculum, slug = slug)
  unit = get_object_or_404(Unit, curriculum = curriculum, slug = unit_slug)

  return render(request, 'curricula/unit.html', {'curriculum': curriculum, 'unit': unit})

def lesson_view(request, slug, unit_slug, lesson_num):
  curriculum = get_object_or_404(Curriculum, slug = slug)
  unit = get_object_or_404(Unit, curriculum = curriculum, slug = unit_slug)
  lesson = get_object_or_404(Lesson.objects.prefetch_related('standards__framework', 'anchor_standards__framework',
                                                             'vocab', 'resources', 'activity_set'),
                             parent = unit, _order = int(lesson_num) - 1)
  page = Page.objects.get(pk = lesson.pk)
  if curriculum.slug == 'csp':
    return render(request, 'curricula/csplesson.html', {'curriculum': curriculum, 'unit': unit, 'lesson': lesson})
  else:
    return render(request, 'curricula/lesson.html', {'curriculum': curriculum, 'unit': unit, 'lesson': lesson})
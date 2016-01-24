from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, render_to_response
from django.conf import settings
from django.contrib.sites.models import get_current_site
#from wkhtmltopdf import WKHtmlToPdf
from cStringIO import StringIO
import pdfkit
import pycurl
#import dryscrape

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from curricula.models import *
from curricula.serializers import *

def index(request):
  curricula = Curriculum.objects.all()
  return render(request, 'curricula/index.html', {'curricula': curricula})

def curriculum_view(request, slug):
  pdf = request.GET.get('pdf', False)
  curriculum = get_object_or_404(Curriculum, slug = slug)

  return render(request, 'curricula/curriculum.html', {'curriculum': curriculum, 'pdf': pdf})

def unit_view(request, slug, unit_slug):
  pdf = request.GET.get('pdf', False)
  curriculum = get_object_or_404(Curriculum, slug = slug)
  unit = get_object_or_404(Unit, curriculum = curriculum, slug = unit_slug)

  return render(request, 'curricula/unit.html', {'curriculum': curriculum, 'unit': unit, 'pdf': pdf})

def lesson_view(request, slug, unit_slug, lesson_num):
  # Why an I doing this here? Can I let the template handle this? Maybe not...
  pdf = request.GET.get('pdf', False)
  lesson = get_object_or_404(Lesson.objects.prefetch_related('standards', 'standards__framework', 'standards__category',
                                                             'standards__category__parent',
                                                             'anchor_standards__framework', 'page_ptr', 'parent',
                                                             'parent__unit', 'parent__unit__curriculum', 'parent__children',
                                                             'vocab', 'resources', 'activity_set'),
                             parent__unit__slug = unit_slug, parent__unit__curriculum__slug = slug,
                             _order = int(lesson_num) - 1)
  if lesson.curriculum.slug == 'csp' or lesson.curriculum.slug == 'algebra' or request.GET.get('csp'):
    template = 'curricula/commonlesson.html'
  elif lesson.curriculum.slug == 'hoc':
    template = 'curricula/hoclesson.html'
  else:
    template = 'curricula/lesson.html'

  return render(request, template, {'curriculum': lesson.curriculum, 'unit': lesson.unit, 'lesson': lesson, 'pdf': pdf})

def lesson_pdf(request, slug, unit_slug, lesson_num):
  buffer = StringIO()
  c = pycurl.Curl()
  c.setopt(c.WRITEDATA, buffer)

  lesson = get_object_or_404(Lesson, parent__unit__slug = unit_slug, parent__unit__curriculum__slug = slug,
                             _order = int(lesson_num) - 1)

  c.setopt(c.URL, get_url_for_pdf(request, lesson.get_absolute_url()))
  print "ready to perform"
  c.perform()
  print 'done'
  c.close()
  print 'closed'

  compiled = buffer.getvalue()
  pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS)

  response = HttpResponse(pdf, content_type='application/pdf')
  response['Content-Disposition'] = 'inline;filename=lesson.pdf'
  return response

def unit_pdf(request, slug, unit_slug):
  buffer = StringIO()
  c = pycurl.Curl()
  c.setopt(c.WRITEDATA, buffer)

  unit = get_object_or_404(Unit, curriculum__slug = slug, slug = unit_slug)

  c.setopt(c.URL, get_url_for_pdf(request, unit.get_absolute_url()))
  c.perform()

  for lesson in unit.lessons:

    c.setopt(c.URL, get_url_for_pdf(request, lesson.get_absolute_url()))
    c.perform()

    '''
    for resource in lesson.resources.all():
      if resource.type != 'video':
        if resource.gd:
          print resource.gd_pdf()
          c.setopt(c.URL, resource.gd_pdf())
          c.perform()
        elif resource.url:
          print resource.url
          c.setopt(c.URL, resource.url)
          c.perform()
    '''

  c.close()
  compiled = buffer.getvalue()
  pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS)

  response = HttpResponse(pdf, content_type='application/pdf')
  response['Content-Disposition'] = 'inline;filename=unit.pdf'
  return response


def curriculum_pdf(request, slug):
  buffer = StringIO()
  c = pycurl.Curl()
  c.setopt(c.WRITEDATA, buffer)

  curriculum = get_object_or_404(Curriculum.objects.prefetch_related('unit_set', 'unit_set__children'), slug = slug)
  print "got the curric"
  c.setopt(c.URL, get_url_for_pdf(request, curriculum.get_absolute_url(), True))
  c.perform()

  for unit in curriculum.unit_set.all():
    print "getting a unit"
    c.setopt(c.URL, get_url_for_pdf(request, unit.get_absolute_url(), True))
    c.perform()
    for lesson in unit.children.all():
      print "getting a lesson"
      c.setopt(c.URL, get_url_for_pdf(request, lesson.lesson.get_absolute_url(), True))
      c.perform()

  c.close()
  compiled = buffer.getvalue()
  pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS)

  if request.GET.get('html'): # Allows testing the html output
    response = HttpResponse(compiled)
  else:
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=curriculum.pdf'
  return response

def get_url_for_pdf(request, abs_url, aws=False):
  # On production we should pull the pages locally to ensure the most recent copy,
  # This causes a crash on local dev, so in that case pull pages from S3
  if aws or settings.ON_PASS:
    print abs_url
    return settings.AWS_BASE_URL + abs_url + '?pdf=true'
  else:
    return 'http://' + get_current_site(request).domain + abs_url + '?pdf=true'

'''
API views

'''

@api_view(['GET',])
def curriculum_list(request, format=None):
  curricula = Curriculum.objects.all()
  serializer = CurriculumSerializer(curricula, many=True)
  return Response(serializer.data)

@api_view(['GET',])
def curriculum_element(request, slug, format=None):
  curriculum = get_object_or_404(Curriculum, slug = slug)

  serializer = CurriculumSerializer(curriculum)
  return Response(serializer.data)

@api_view(['GET',])
def unit_list(request, slug, format=None):
  curriculum = get_object_or_404(Curriculum, slug = slug)

  units = curriculum.units
  serializer = UnitSerializer(units, many=True)
  return Response(serializer.data)

@api_view(['GET',])
def unit_element(request, slug, unit_slug, format=None):
  curriculum = get_object_or_404(Curriculum, slug = slug)

  unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)

  serializer = UnitSerializer(unit)
  return Response(serializer.data)

@api_view(['GET',])
def api_root(request, format=None):
  return Response({
    'curriculum': reverse('curriculum_list', request=request, format=format)
  })

@api_view(['GET',])
def lesson_element(request, slug, unit_slug, lesson_num):
  curriculum = get_object_or_404(Curriculum, slug = slug)

  unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)
  lesson = get_object_or_404(Lesson.objects.prefetch_related('standards__framework', 'anchor_standards__framework',
                                                             'vocab', 'resources', 'activity_set'),
                             parent = unit, _order = int(lesson_num) - 1)

  serializer = LessonSerializer(lesson)
  return Response(serializer.data)

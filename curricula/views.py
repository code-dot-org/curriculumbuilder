from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.contrib.admin.views.decorators import staff_member_required
from mezzanine.core.views import edit
from django.template.loader import render_to_string
# from wkhtmltopdf import WKHtmlToPdf
from cStringIO import StringIO
import pdfkit
import pycurl
import logging
import json
import sys
import pprint
from PyPDF2 import PdfFileReader, PdfFileMerger
from urllib2 import Request, urlopen
# import dryscrape

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework import generics
from rest_framework import viewsets


import reversion
from reversion.views import create_revision

from curricula.models import *
from curricula.serializers import *

def index(request):
  if (request.user.is_staff):
    curricula = Curriculum.objects.all()
  else:
    curricula = Curriculum.objects.filter(login_required=False)


  return render(request, 'curricula/index.html', {'curricula': curricula})

'''
Core curricula and lesson views

'''


def curriculum_view(request, slug):
  pdf = request.GET.get('pdf', False)
  curriculum = get_object_or_404(Curriculum, slug = slug)
  if (request.user.is_staff):
    units = Unit.objects.filter(curriculum = curriculum)
  else:
    units = Unit.objects.filter(curriculum = curriculum, login_required=False)

  return render(request, 'curricula/curriculum.html', {'curriculum': curriculum, 'pdf': pdf, 'units': units})


def unit_view(request, slug, unit_slug):
  pdf = request.GET.get('pdf', False)
  if pdf:
    template = 'curricula/unit_lessons.html'
  else:
    template = 'curricula/unit.html'

  curriculum = get_object_or_404(Curriculum, slug = slug)
  if (request.user.is_staff):
    unit = get_object_or_404(Unit, curriculum = curriculum, slug = unit_slug)
  else:
    unit = get_object_or_404(Unit, curriculum = curriculum, slug = unit_slug, login_required=request.user.is_staff)

  return render(request, template, {'curriculum': curriculum, 'unit': unit, 'pdf': pdf})


def chapter_view(request, slug, unit_slug, chapter_num):
  pdf = request.GET.get('pdf', False)
  curriculum = get_object_or_404(Curriculum, slug = slug)
  unit = get_object_or_404(Unit, curriculum = curriculum, slug = unit_slug)
  chapter = get_object_or_404(Chapter, parent__unit = unit, number = chapter_num)

  return render(request, 'curricula/chapter.html', {'curriculum': curriculum, 'unit': unit, 'chapter': chapter, 'pdf': pdf})


def lesson_view(request, slug, unit_slug, lesson_num, optional_num=False):

  pdf = request.GET.get('pdf', False)
  parent = None
  optional = False

  if optional_num:
    optional = True
    lesson = get_object_or_404(Lesson.objects.prefetch_related('standards', 'standards__framework', 'standards__category',
                                                               'standards__category__parent',
                                                               'anchor_standards__framework', 'page_ptr', 'parent',
                                                               'parent__unit', 'parent__unit__curriculum', 'parent__children',
                                                               'vocab', 'resources', 'activity_set'),
                               unit__slug = unit_slug, unit__curriculum__slug = slug, parent__lesson__number = lesson_num, number = optional_num)
    parent = lesson.parent.lesson
    if hasattr(lesson.parent.parent, 'chapter'):
      chapter = lesson.parent.parent.chapter
    else:
      chapter = None

  else:
    lesson = get_object_or_404(Lesson.objects.prefetch_related('standards', 'standards__framework', 'standards__category',
                                                               'standards__category__parent',
                                                               'anchor_standards__framework', 'page_ptr', 'parent',
                                                               'parent__unit', 'parent__unit__curriculum', 'parent__children',
                                                               'vocab', 'resources', 'activity_set'),
                               unit__slug = unit_slug, unit__curriculum__slug = slug, number = lesson_num, parent__lesson__isnull=True)
    if hasattr(lesson.parent, 'chapter'):
      chapter = lesson.parent.chapter
    else:
      chapter = None

  '''
  if request.GET.get('codestudio', False):
    template = 'curricula/codestudiolesson.html'
  else:
    template = 'curricula/commonlesson.html'
  '''

  template = 'curricula/codestudiolesson.html'

  return render(request, template, {'curriculum': lesson.curriculum, 'unit': lesson.unit, 'chapter': chapter, 'lesson': lesson,
                                    'pdf': pdf, 'parent': parent, 'optional':optional})

def lesson_markdown(request, slug, unit_slug, lesson_num):

  lesson = get_object_or_404(Lesson, unit__slug = unit_slug, unit__curriculum__slug = slug, number = lesson_num, parent__lesson__isnull=True)

  return render(request, 'curricula/lesson-overview.md', {'lesson': lesson}, content_type='text/markdown')
'''
Resource list views
'''

def curriculum_resources(request, slug):
  curriculum = Curriculum.objects.get(slug = slug)
  return render(request, 'curricula/resources_curriculum.html', {'curriculum': curriculum})

'''
PDF rendering views

'''

def lesson_pdf(request, slug, unit_slug, lesson_num):
  buffer = StringIO()
  c = pycurl.Curl()
  c.setopt(c.WRITEDATA, buffer)

  lesson = get_object_or_404(Lesson, unit__slug = unit_slug, unit__curriculum__slug = slug, number = lesson_num, parent__lesson__isnull=True)

  c.setopt(c.URL, get_url_for_pdf(request, lesson.get_absolute_url()) + "?pdf=true")
  print "ready to perform"
  c.perform()
  print 'done'
  c.close()
  print 'closed'

  compiled = buffer.getvalue()

  if request.GET.get('html'): # Allows testing the html output
    response = HttpResponse(compiled)
  else:
    pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=lesson.pdf'
  return response

def unit_pdf(request, slug, unit_slug):
  buffer = StringIO()
  c = pycurl.Curl()
  c.setopt(c.WRITEDATA, buffer)

  unit = get_object_or_404(Unit, curriculum__slug=slug, slug=unit_slug)

  c.setopt(c.URL, get_url_for_pdf(request, unit.get_absolute_url(), True))
  c.perform()

  c.close()
  compiled = buffer.getvalue()

  if request.GET.get('html'): # Allows testing the html output
    response = HttpResponse(compiled)
  else:
    pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=unit%s.pdf' % unit.number
  return response

def unit_resources_pdf(request, slug, unit_slug):
  merger = PdfFileMerger()
  unit = get_object_or_404(Unit, curriculum__slug=slug, slug=unit_slug)
  for lesson in unit.lessons.exclude(keywords__keyword__slug="optional"):
    lesson_string = render_to_string("curricula/lesson_title.html", {'unit': unit, 'lesson': lesson}, request=request)
    lesson_page = pdfkit.from_string(lesson_string, False, options=settings.WKHTMLTOPDF_CMD_OPTIONS)
    lesson_page_pdf = StringIO(lesson_page)
    merger.append(PdfFileReader(lesson_page_pdf))
    for resource in lesson.resources.all():
      if resource.gd:
        try:
          remotePDF = urlopen(Request(resource.gd_pdf())).read()
          memoryPDF = StringIO(remotePDF)
          localPDF = PdfFileReader(memoryPDF)
          merger.append(localPDF)
        except:
          logging.error('Failed to open resource: %s - %s (pk %s)' % (resource.name, resource.type, resource.pk))
  response = HttpResponse(content_type='application/pdf')
  merger.write(response)
  response['Content-Disposition'] = 'inline;filename=unit%s_resources.pdf' % unit.number
  return response


def curriculum_pdf(request, slug):
  buffer = StringIO()
  c = pycurl.Curl()
  c.setopt(c.WRITEDATA, buffer)

  curriculum = get_object_or_404(Curriculum.objects.prefetch_related('unit_set', 'unit_set__children'), slug = slug)

  c.setopt(c.URL, get_url_for_pdf(request, curriculum.get_absolute_url(), False))
  c.perform()

  for unit in curriculum.unit_set.all():
    c.setopt(c.URL, get_url_for_pdf(request, unit.get_absolute_url(), False))
    c.perform()
    for lesson in unit.children.all():
      c.setopt(c.URL, get_url_for_pdf(request, lesson.lesson.get_absolute_url(), False))
      c.perform()

  c.close()
  compiled = buffer.getvalue()

  if request.GET.get('html'): # Allows testing the html output
    response = HttpResponse(compiled)
  else:
    pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=curriculum.pdf'
  return response

def get_url_for_pdf(request, abs_url, aws=False):
  # On production we should pull the pages locally to ensure the most recent copy,
  # This causes a crash on local dev, so in that case pull pages from S3
  '''
  if False: #aws or not settings.ON_PAAS:
    print abs_url
    return settings.AWS_BASE_URL + abs_url + '?pdf=true'
  else:
    return 'http://' + get_current_site(request).domain + abs_url + '?pdf=true'
  '''
  return 'http://%s%s?pdf=true' % (get_current_site(request).domain, abs_url)

'''
Publishing views

'''

@staff_member_required
def publish(request):
  try:
    pk = int(request.POST.get('pk'))
    type = request.POST.get('type')
    if request.POST.get('lessons') == 'true':
      children = True
    else:
      children = False
    klass = globals()[type]
    object = klass.objects.get(pk=pk)
    payload = object.publish(children)
  except:
    payload = {'error': 'failed'}
  print payload
  return HttpResponse(json.dumps(payload), content_type='application/json')


@staff_member_required
def get_stage_details(request):
  try:
    pk = int(request.POST.get('pk'))
    lesson = Lesson.objects.get(pk=pk)
    print lesson
    if not hasattr(lesson.unit, 'stage_name'):
      payload = {'error': 'No stage name for unit'}
    else:
      lesson.save()
      payload = {'success': 'true'}
  except:
    payload = {'error': 'failed'}
  print payload
  return HttpResponse(json.dumps(payload), content_type='application/json')


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

'''
class AnnotationList(generics.ListCreateAPIView):
  queryset = Annotation.objects.all()
  serializer_class = AnnotationSerializer

class AnnotationMember(generics.RetrieveUpdateDestroyAPIView):
  queryset = Annotation.objects.all()
  serializer_class = AnnotationSerializer
'''


class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer


class AnnotationListCreateView(generics.ListCreateAPIView):
    queryset = Annotation.objects.all()
    filter_fields = ('uri', 'owner', 'lesson')
    serializer_class = AnnotationSerializer


class AnnotationSearchView(generics.ListCreateAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def list(self, request):
        lesson = self.request.query_params.get('lesson', None)

        if lesson is None:
            return Response({"Require lesson to filter results"})
        else:
            queryset = Annotation.objects.filter(lesson=lesson)
            serializer = AnnotationSerializer(queryset, many=True)
            return Response({'rows': serializer.data, 'total': len(serializer.data)})


class AnnotationReadUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer


@create_revision()
def reversion_edit(request):

    reversion.set_comment("Changed %s of %s from frontend" % (request.POST.get("fields"), request.POST.get("model")))
    response = edit(request)
    return response

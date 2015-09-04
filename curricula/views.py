from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.shortcuts import get_object_or_404, render, render_to_response
from django.conf import settings
#from wkhtmltopdf import WKHtmlToPdf
from cStringIO import StringIO
import pdfkit
import pycurl
#import dryscrape

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
  pdf = request.GET.get('pdf', False)
  curriculum = get_object_or_404(Curriculum, slug = slug)
  unit = get_object_or_404(Unit, curriculum = curriculum, slug = unit_slug)
  lesson = get_object_or_404(Lesson.objects.prefetch_related('standards__framework', 'anchor_standards__framework',
                                                             'vocab', 'resources', 'activity_set'),
                             parent = unit, _order = int(lesson_num) - 1)
  page = Page.objects.get(pk = lesson.pk)
  if curriculum.slug == 'csp' or curriculum.slug == 'algebra':
    template = 'curricula/csplesson.html'
  elif curriculum.slug == 'hoc':
    template = 'curricula/hoclesson.html'
  else:
    template = 'curricula/lesson.html'

  return render(request, template, {'curriculum': curriculum, 'unit': unit, 'lesson': lesson, 'pdf': pdf})

def curriculum_pdf(request, slug):
  buffer = StringIO()
  c = pycurl.Curl()
  c.setopt(c.WRITEDATA, buffer)
  #session = dryscrape.Session()


  curriculum = get_object_or_404(Curriculum, slug = slug)
  for unit in curriculum.units():
    for lesson in unit.lessons():

      print lesson.title
      #c.setopt(c.URL, settings.AWS_BASE_URL + lesson.get_absolute_url() + '?pdf=true')
      c.setopt(c.URL, lesson.get_absolute_url_with_host() + '?pdf=true')
      c.perform()
      #session.visit(settings.AWS_BASE_URL + lesson.get_absolute_url())
      #compiled += session.body()

  c.close()
  compiled = buffer.getvalue()
  pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS)

  response = HttpResponse(pdf, content_type='application/pdf')
  response['Content-Disposition'] = 'inline;filename=curriculum.pdf'
  #response = HttpResponse("testing a thing")
  return response


'''
def lesson_pdf(request, slug, unit_slug, lesson_num):
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition' = 'attachment; filename="lesson.pdf"']
  wkhtmltopdf = WKHtmlToPdf(
    url='http://localhost:8000/curriculum/csp/unit1/1/?pdf=true',
    output_file='csp.pdf',
    s="Letter",
    print_media_type=True)
  return wkhtmltopdf.render()
'''
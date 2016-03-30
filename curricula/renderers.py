from django_medusa.renderers import StaticSiteRenderer
from curricula.models import Curriculum
from standards.models import Framework

class CurriculumRenderer(StaticSiteRenderer):
  def get_paths(self):
    paths = set(["/curriculum/",])
    for curriculum in Curriculum.objects.all():
      paths.add(curriculum.get_absolute_url())
      paths.add(curriculum.get_absolute_url() + "standards/")
      for unit in curriculum.units:
        paths.add(unit.get_absolute_url())
        paths.add(unit.get_absolute_url() + "standards/")
        for lesson in unit.lessons:
          paths.add(lesson.get_absolute_url())
    return list(paths)

class JSONRenderer(StaticSiteRenderer):
  def get_paths(self):
    baseurl = "/api/v1/"
    paths = set([baseurl, baseurl + "curriculum/"])
    for curriculum in Curriculum.objects.all():
      paths.add(baseurl + "curriculum/" + curriculum.slug + "/")
      paths.add(baseurl + "curriculum/" + curriculum.slug + "/standards/")


      # This feels hacky, but seems to work...
      '''
      for framework in Framework.objects.filter(category__standard__lesson__parent__parent=curriculum).values_list('slug', flat=True).distinct():
        print baseurl + "curriculum/" + curriculum.slug + "/standards/" + framework + "/"
        paths.add(paths.add(baseurl + "curriculum/" + curriculum.slug + "/standards/" + framework + "/"))
      '''

    paths.add(baseurl + "curriculum/" + curriculum.slug + "/standards/CSP/")
    return list(paths)

class PDFRenderer(StaticSiteRenderer):
  def get_paths(self):
    paths = set([])
    for curriculum in Curriculum.objects.all():
      paths.add(curriculum.get_absolute_url() + 'pdf')
    return list(paths)

renderers = [CurriculumRenderer, JSONRenderer, PDFRenderer]
#renderers = [JSONRenderer, ]
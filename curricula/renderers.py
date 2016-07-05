from django_medusa.renderers import StaticSiteRenderer
from curricula.models import Curriculum
from standards.models import Framework

class CurriculumRenderer(StaticSiteRenderer):
  def get_paths(self):
    paths = set(["/",])
    for curriculum in Curriculum.objects.filter(status=2): # status 2 means published
      print curriculum, curriculum.pk
      paths.add(curriculum.get_absolute_url())
      paths.add(curriculum.get_absolute_url() + "standards/")
      for unit in curriculum.units:
        print unit, unit.pk
        if unit.status == 2:
          paths.add(unit.get_absolute_url())
          paths.add(unit.get_absolute_url() + "standards/")
        for chapter in unit.chapters:
          print chapter, chapter.pk
          if chapter.status == 2: paths.add(chapter.get_absolute_url())
        for lesson in unit.lessons:
          print lesson, lesson.pk
          if lesson.status == 2: paths.add(lesson.get_absolute_url())
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
    for unit in Unit.objects.all():
      paths.add(unit.get_absolute_url() + 'pdf')
    return list(paths)

renderers = [PDFRenderer]
#renderers = [JSONRenderer, ]
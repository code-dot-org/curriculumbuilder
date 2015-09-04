from django_medusa.renderers import StaticSiteRenderer
from curricula.models import Curriculum

class CurriculumRenderer(StaticSiteRenderer):
  def get_paths(self):
    paths = set(["/curriculum/",])
    for curriculum in Curriculum.objects.all():
      paths.add(curriculum.get_absolute_url())
      for unit in curriculum.units():
        paths.add(unit.get_absolute_url())
        for lesson in unit.lessons():
          paths.add(lesson.get_absolute_url())
    return list(paths)

class PDFRenderer(StaticSiteRenderer):
  def get_paths(self):
    paths = set([])
    for curriculum in Curriculum.objects.all():
      paths.add(curriculum.get_absolute_url() + 'pdf')
    return list(paths)

renderers = [CurriculumRenderer, PDFRenderer]
from django.core.urlresolvers import reverse
from jackfrost.models import ModelRenderer
from curricula.models import *
from lessons.models import *

#def homeRenderer():
#    return [reverse('curriculum:home')]

class CurriculumRenderer(ModelRenderer):
  def get_model(self):
    return Curriculum

  def get_queryset(self):
    return self.get_model().objects.filter(status=2, login_required=False)

class UnitRenderer(ModelRenderer):
  def get_model(self):
    return Unit

  def get_queryset(self):
    return self.get_model().objects.filter(status=2, login_required=False)

class ChapterRenderer(ModelRenderer):
  def get_model(self):
    return Chapter

  def get_queryset(self):
    return self.get_model().objects.filter(status=2, login_required=False)

class LessonRenderer(ModelRenderer):
  def get_model(self):
    return Lesson

  def get_queryset(self):
    return self.get_model().objects.filter(status=2, login_required=False)

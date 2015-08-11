from django.db import models
from mezzanine.pages.models import Page, RichText, Orderable
from mezzanine.core.fields import RichTextField
from standards.models import Standard, GradeBand
from lessons.models import Lesson

"""
Curriculum

"""
class Curriculum(Page, RichText):
  gradeband = models.ForeignKey(GradeBand)

  def __unicode__(self):
    return self.title

  class Meta:
      verbose_name_plural = "curricula"

"""
Curricular Unit

"""
class Unit(Page, RichText):
  curriculum = models.ForeignKey(Curriculum, blank=True, null=True)

  def __unicode__(self):
    return self.title

  def number(self):
    return self._order + 1

  def lessons(self):
    return Lesson.objects.filter(parent=self)

  def save(self, *args, **kwargs):
    try:
      self.curriculum = self.parent.curriculum
    except:
      return
    super(Unit, self).save(*args, **kwargs)

"""
Intermediary Model for lessons
Deprecated

class UnitLesson(Orderable):
  unit = models.ForeignKey(Unit)
  lesson = models.ForeignKey(Lesson)

  def __unicode__(self):
    return self.lesson.title

  def url(self):
    return self.lesson.get_absolute_url()
"""
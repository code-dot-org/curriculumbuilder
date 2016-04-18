from django.db import models
from django.utils.text import slugify
from mezzanine.pages.models import Page, RichText, Orderable
from mezzanine.core.fields import RichTextField
from standards.models import Standard, GradeBand
import lessons.models

"""
Curriculum

"""
class Curriculum(Page, RichText):
  gradeband = models.ForeignKey(GradeBand)

  class Meta:
      verbose_name_plural = "curricula"

  def __unicode__(self):
    return self.title

  def get_absolute_url(self):
    return '/curriculum/' + self.slug + '/'

  @property
  def units(self):
    return Unit.objects.filter(parent=self)

"""
Curricular Unit

"""
class Unit(Page, RichText):
  curriculum = models.ForeignKey(Curriculum, blank=True, null=True)
  number =  models.IntegerField('Number', blank=True, null=True)


  def __unicode__(self):
    return self.title

  def get_absolute_url(self):
    return self.curriculum.get_absolute_url() + self.slug + '/'

  def get_number(self):
    return self._order + 1

  @property
  def lessons(self):
    return self.lesson_set.all()

  def save(self, *args, **kwargs):

    if not self.slug:
      self.slug = slugify(self.title)[:255]
    try:
      self.curriculum = self.parent.curriculum
    except:
      return
    self.number = self.get_number()
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
from django.db import models
from django.utils.text import slugify
from mezzanine.pages.models import Page, RichText, Orderable
from mezzanine.core.fields import RichTextField
from standards.models import Standard, GradeBand, Category
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
    return '/%s/' %(self.slug)

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
    return int(self._order) + 1

  @property
  def lessons(self):
    return self.lesson_set.all()

  @property
  def chapters(self):
    return Chapter.objects.filter(parent__unit=self)

  def save(self, *args, **kwargs):

    if not self.slug:
      self.slug = slugify(self.title)[:255]
    try:
      self.curriculum = self.parent.curriculum
    except:
      return
    try:
      self.number = self.get_number()
    except:
      self.number = self.curriculum.units.count() + 1
    super(Unit, self).save(*args, **kwargs)

"""
Unit Chapter

"""
class Chapter(Page, RichText):
  number = models.IntegerField('Number', blank=True, null=True)
  questions = RichTextField(blank=True, null=True, help_text="md list of big questions")
  understandings = models.ManyToManyField(Category, blank=True)
  _old_slug = models.CharField('old_slug', max_length=2000, blank=True, null=True)

  def __unicode__(self):
    return self.title

  def get_absolute_url(self):
    return "%sch%s/" %(self.unit.get_absolute_url(), str(self.number))

  def get_number(self):
    return int(self._order) + 1

  @property
  def unit(self):
    return self.parent.unit

  @property
  def lessons(self):
    return lessons.models.Lesson.objects.filter(parent__chapter = self)

  def save(self, *args, **kwargs):

    if not self.slug:
      self.slug = slugify(self.title)[:255]
    try:
      self.number = self.get_number()
    except:
      self.number = self.unit.chapters.count() + 1
    super(Chapter, self).save(*args, **kwargs)

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
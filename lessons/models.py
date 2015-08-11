from django.db import models
from mezzanine.pages.models import Page, RichText, Orderable
from mezzanine.core.fields import RichTextField
from standards.models import Standard

"""
Vocabulary

"""
class Vocab(models.Model):
  word = models.CharField(max_length=255)
  simpleDef = models.TextField()
  detailDef = models.TextField(blank=True, null=True)

  class Meta:
      ordering = ["word"]
      verbose_name_plural = "vocab words"

  def __unicode__(self):
    return self.word

  def save(self, *args, **kwargs):
    if not self.detailDef:
      self.detailDef = self.simpleDef
    super(Vocab, self).save(*args, **kwargs)

"""
Linked Resources

"""
class Resource(models.Model):
  name = models.CharField(max_length=255)
  type = models.CharField(max_length=255, blank=True, null=True)
  student = models.BooleanField(default=False)
  url = models.URLField(blank=True, null=True)

  def __unicode__(self):
    return self.name

"""
Complete Lesson Page

"""
class Lesson(Page, RichText):
  overview = RichTextField('Lesson Overview')
  duration = models.IntegerField('Class Periods', blank=True, null=True)
  unplugged = models.BooleanField(default=False)
  resources = models.ManyToManyField(Resource, blank=True)
  prep = RichTextField('Materials and Prep', blank=True, null=True)
  cs_content = RichTextField('CS Content', blank=True, null=True)
  ancestor = models.ForeignKey('self', blank=True, null=True)
  standards = models.ManyToManyField(Standard, blank=True)
  anchor_standards = models.ManyToManyField(Standard, related_name="anchors", blank=True)
  vocab = models.ManyToManyField(Vocab, blank=True)
  _old_slug = models.CharField('old_slug', max_length=2000, blank=True, null=True)

  def __unicode__(self):
    return self.title

  class Meta:
    ordering = ["_order"]

  def unit(self):
    return self.parent.unit

  def curriculum(self):
    return self.parent.curriculum

  def number(self):
    return self._order + 1

  def get_absolute_url(self):
    return '/curriculum/' + self.curriculum().slug + '/' + self.unit().slug + '/' + str(self.number())

"""
Activities that compose a lesson

"""
class Activity(Orderable):
  name = models.CharField(max_length=255)
  content = RichTextField('Activity Content')
  lesson = models.ForeignKey(Lesson)
  ancestor = models.ForeignKey('self', blank=True, null=True)

  class Meta:
      verbose_name_plural = "activities"

  def __unicode__(self):
    return self.name

"""
Prerequisite Skills

"""
class Prereq(Orderable):
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True, null=True)
  lesson = models.ForeignKey(Lesson)

  def __unicode__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.description:
      self.description = self.name
    super(Prereq, self).save(*args, **kwargs)

"""
Learning Objectives

"""
class Objective(Orderable):
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True, null=True)
  lesson = models.ForeignKey(Lesson)

  def __unicode__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.description:
      self.description = self.name
    super(Objective, self).save(*args, **kwargs)

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
  detailDef = models.TextField()

  def __unicode__(self):
    return self.word

"""
Complete Lesson Page

"""
class Lesson(Orderable):
  overview = RichTextField('Lesson Overview')
  duration = models.IntegerField('Class Periods')
  unplugged = models.BooleanField(default=False)
  resources = RichTextField(blank=True, null=True)
  ancestor = models.ForeignKey('self', blank=True, null=True)
  standards = models.ManyToManyField(Standard, related_name="standards", blank=True, null=True)
  anchor_standards = models.ManyToManyField(Standard, related_name="anchor_standards", blank=True, null=True)
  vocab = models.ManyToManyField(Vocab)

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
  description = models.TextField()
  lesson = models.ForeignKey(Lesson)

  def __unicode__(self):
    return self.name

"""
Learning Objectives

"""
class Objective(Orderable):
  name = models.CharField(max_length=255)
  description = models.TextField()
  lesson = models.ForeignKey(Lesson)

  def __unicode__(self):
    return self.name
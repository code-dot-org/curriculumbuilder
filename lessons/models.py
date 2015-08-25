import re
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
  mathy = models.BooleanField(default=False)

  class Meta:
      ordering = ["word"]
      verbose_name_plural = "vocab words"

  def __unicode__(self):
    if self.mathy:
      return self.word + ' (math)' + ': ' + self.simpleDef
    else:
      return self.word + ': ' + self.simpleDef

  def save(self, *args, **kwargs):
    if not self.detailDef:
      self.detailDef = self.simpleDef
    super(Vocab, self).save(*args, **kwargs)

"""
Linked Resources

"""
class Resource(models.Model):
  name = models.CharField(max_length=255, unique=True)
  type = models.CharField(max_length=255, blank=True, null=True)
  student = models.BooleanField('Student Facing', default=False)
  gd = models.BooleanField('Google Doc', default=False)
  url = models.URLField(blank=True, null=True)
  dl_url = models.URLField('Download URL', help_text='Alternate download url', blank=True, null=True)

  class Meta:
    ordering = ['student', 'type']

  def __unicode__(self):
    if self.url:
      formatted = "<a href='%s' target='_blank'>%s</a> - %s" % (self.url, self.name, self.type)
    else:
      formatted = "%s - %s" % (self.name, self.type)
    if self.dl_url:
      formatted = "%s (<a href='%s'>download</a>)" % (formatted, self.dl_url)
    elif self.gd:
      formatted = "%s (<a href='%s'>download</a>)" % (formatted, self.gd_pdf())
    return formatted

  def gd_pdf(self):
    try:
      pdf = re.search(r'^(.*[/])', self.url).group()
      pdf = pdf + 'export?format=pdf'
      return pdf
    except:
      return self.url

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

  class Meta:
    ordering = ["_order"]

  def __unicode__(self):
    return self.title

  def get_absolute_url(self):
    return self.unit().get_absolute_url() + str(self.number()) + '/'

  def unit(self):
    return self.parent.unit

  def curriculum(self):
    return self.parent.unit.curriculum

  def number(self):
    return self._order + 1

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

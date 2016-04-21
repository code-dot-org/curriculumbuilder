import re
import itertools
import datetime
import urllib2
from urlparse import urlparse
from copy import copy, deepcopy
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from mezzanine.pages.models import Page, RichText, Orderable
from mezzanine.core.fields import RichTextField
from mezzanine.generic.fields import CommentsField
from standards.models import Standard
import curricula.models

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
  name = models.CharField(max_length=255)
  type = models.CharField(max_length=255, blank=True, null=True)
  student = models.BooleanField('Student Facing', default=False)
  gd = models.BooleanField('Google Doc', default=False)
  url = models.URLField(blank=True, null=True)
  dl_url = models.URLField('Download URL', help_text='Alternate download url', blank=True, null=True)
  slug = models.CharField(max_length=255, unique=True, blank=True, null=True)

  class Meta:
    ordering = ['name',]

  def __unicode__(self):
    '''
    if self.url:
      formatted = "<a href='%s' target='_blank' class='print_link'>%s</a> - %s" % (self.url, self.name, self.type)
    else:
      formatted = "%s - %s" % (self.name, self.type)
    if self.dl_url:
      formatted = "%s (<a href='%s' class='print_link'>download</a>)" % (formatted, self.dl_url)
    elif self.gd:
      formatted = "%s (<a href='%s' class='print_link'>download</a>)" % (formatted, self.gd_pdf())
    '''
    if (self.type):
      return "%s - %s" % (self.name, self.type)
    else:
      return self.name

  def formatted(self):
    if self.url:
      formatted = "<a href='%s' target='_blank' class='print_link'>%s</a>" % (self.fallback_url(), self.name)
    else:
      formatted = self.name
    if self.type:
      formatted = "%s - %s" % (formatted, self.type)
    if self.dl_url:
      formatted = "%s (<a href='%s' class='print_link'>download</a>)" % (formatted, self.dl_url)
    elif self.gd:
      formatted = "%s (<a href='%s' class='print_link'>download</a>)" % (formatted, self.gd_pdf())
    return formatted

  # If resource lives on pegasus check to see if it's on prod, otherwise fallback to staging
  def fallback_url(self):
    parsed = urlparse(self.url)
    if parsed.netloc == 'code.org':
      try:
        urllib2.urlopen(parsed.geturl())
        return self.url
      except:
        return '%s://staging.%s%s' % (parsed.scheme, parsed.netloc, parsed.path )
    else:
      return self.url

  def md_tag(self):
    if self.slug:
      return '[r ' + self.slug + ']'
    else:
      return '[r ' + self.name + ']'

  def gd_pdf(self):
    try:
      pdf = re.search(r'^(.*[/])', self.url).group()
      pdf = pdf + 'export?format=pdf'
      return pdf
    except:
      return self.url

  def save(self, *args, **kwargs):

    if not self.slug:
      self.slug = slugify(self.name)[:255]

      # Check for slug uniqueness, if not unique append number
      for x in itertools.count(1):
        if not Resource.objects.filter(slug=self.slug):
          break
        self.slug = '%s-%d' % (self.slug[:250], x)

    super(Resource, self).save(*args, **kwargs)

"""
Complete Lesson Page

"""
class Lesson(Page, RichText):
  overview = RichTextField('Lesson Overview')
  duration = models.IntegerField('Week', help_text='Week number within the unit', blank=True, null=True)
  unplugged = models.BooleanField(default=False)
  resources = models.ManyToManyField(Resource, blank=True)
  prep = RichTextField('Preparation', help_text='ToDos for the teacher to prep this lesson', blank=True, null=True)
  cs_content = RichTextField('Purpose', help_text='Purpose of this lesson in connection to greater CS concepts and its role in the progression', blank=True, null=True)
  ancestor = models.ForeignKey('self', blank=True, null=True)
  standards = models.ManyToManyField(Standard, blank=True)
  anchor_standards = models.ManyToManyField(Standard, help_text='1 - 3 key standards this lesson focuses on', related_name="anchors", blank=True)
  vocab = models.ManyToManyField(Vocab, blank=True)
  comments = CommentsField()
  unit = models.ForeignKey(curricula.models.Unit, blank=True, null=True)
  curriculum = models.ForeignKey(curricula.models.Curriculum, blank=True, null=True)
  number = models.IntegerField('Number', blank=True, null=True)
  _old_slug = models.CharField('old_slug', max_length=2000, blank=True, null=True)

  class Meta:
    ordering = ["number"]

  def __unicode__(self):
    return self.title

  def __deepcopy(self):
    lesson_copy = self
    lesson_copy.pk = None
    # deepcopy page, activities, prereqs, and objectives
    lesson_copy.save()
    return lesson_copy

  def get_absolute_url(self):
    return self.unit.get_absolute_url() + str(self.number) + '/'

  def get_unit(self):
    try:
      return self.parent.unit
    except:
      return self.parent.parent.unit # If under a chapter

  def save(self, *args, **kwargs):
    self.unit = self.get_unit()
    self.curriculum = self.get_curriculum()
    try:
      self.number = self.get_number()
    except:
      self.number = self.unit.lessons.count() + 1
    super(Lesson, self).save(*args, **kwargs)

  def get_number(self):
    order = 1
    if hasattr(self.parent, 'unit'):
      return order + int(self._order)
    else:
      chapter = self.parent
      chapter_count = chapter._order

      while chapter_count > 0:
        chapter = chapter.get_previous_by_order()
        order += chapter.children.count()
        chapter_count = chapter._order

      return order + int(self._order)

  def get_curriculum(self):
    return self.unit.curriculum

"""
Activities that compose a lesson

"""
class Activity(Orderable):
  name = models.CharField(max_length=255)
  content = RichTextField('Activity Content')
  time = models.CharField(max_length=255, blank=True, null=True)
  lesson = models.ForeignKey(Lesson)
  ancestor = models.ForeignKey('self', blank=True, null=True)

  class Meta:
      verbose_name_plural = "activities"

  def __unicode__(self):
    if self.time:
      return "%s (%s)" % (self.name, self.time)
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

"""
Annotations

"""
class Annotation(models.Model):
    lesson = models.ForeignKey('Lesson', related_name='%(class)s_parent_lesson_relation')
    owner = models.ForeignKey(User, related_name='%(class)s_creator_relation')

    # Key fields from the Annotator JSON Format: http://docs.annotatorjs.org/en/latest/annotation-format.html
    annotator_schema_version = models.CharField(max_length=8, blank=True)
    text = models.TextField(blank=True)
    quote = models.TextField()
    uri = models.URLField(blank=True, null=True)
    range_start = models.TextField()
    range_end = models.TextField()
    range_startOffset = models.BigIntegerField()
    range_endOffset = models.BigIntegerField()

    # Created/Modified
    # See this for background:
    # http://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add/1737078#1737078
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.created = datetime.datetime.today()
        self.modified = datetime.datetime.today()
        return super(Annotation, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.lesson.title + ":'" + self.quote + "'"

    def ranges(self):
        return [self.range_start, self.range_end, self.range_startOffset, self.range_endOffset]
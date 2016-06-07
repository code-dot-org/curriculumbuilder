from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from mezzanine.pages.models import Page, RichText, Orderable
from mezzanine.core.fields import RichTextField
from jackfrost.utils import build_page_for_obj
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

    # TODO: Need to make this logic more robust
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
  def curriculum(self):
    return self.unit.curriculum

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
These post_save receivers calls the JackFrost build command
to automatically publish pages on save, as long as they
are marked publish (status == 2) and do not require a login to view.
We also kick off a save for the parent page (curric, unit, chapter)
if applicable to ensure listing pages are updated.

"""
@receiver(post_save, sender=Curriculum)
def curriculum_handler(sender, instance, **kwargs):
  if instance.status == 2 and not instance.login_required:
    try:
      build_page_for_obj(sender, instance, **kwargs)
    except:
      pass
  else:
    return

@receiver(post_save, sender=Unit)
def unit_handler(sender, instance, **kwargs):
  if instance.status == 2 and not instance.login_required:
    try:
      build_page_for_obj(sender, instance, **kwargs)
      instance.curriculum.save()
    except:
      pass
  else:
    return

@receiver(post_save, sender=Chapter)
def chapter_handler(sender, instance, **kwargs):
  if instance.status == 2 and not instance.login_required:
    try:
      build_page_for_obj(sender, instance, **kwargs)
      instance.unit.save()
    except:
      pass
  else:
    return
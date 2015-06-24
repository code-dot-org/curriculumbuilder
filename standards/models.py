from django.db import models

"""
Top level of a standards framework

"""
class Framework(models.Model):
  name = models.CharField(max_length=255)
  slug = models.SlugField()
  description = models.TextField()
  website = models.URLField()

  def __unicode__(self):
    return self.name

"""
Generic standards category to allow for various
standards framework structures.
Can be related to another upstream category,
or a Framework if this is the top level category.

Type should be set to the name appropriate for each framework

"""
class Category(models.Model):
  name = models.CharField(max_length=255)
  shortcode = models.CharField(max_length=50)
  description = models.TextField(blank=True, null=True)
  type = models.CharField(max_length=50, blank=True, null=True)
  framework = models.ForeignKey(Framework, blank=True, null=True)
  parent = models.ForeignKey('self', blank=True, null=True, related_name="children")

  def __unicode__(self):
    return self.name

  class Meta:
      ordering = ["shortcode"]
      verbose_name_plural = "categories"

"""
Individual grades which make up a GradeBand

"""
class Grade(models.Model):
  name = models.CharField(max_length=255)

  def __unicode__(self):
    return self.name

"""
A collection of grades to which a standard can belong

"""
class GradeBand(models.Model):
  name = models.CharField(max_length=255)
  shortcode = models.CharField(max_length=50, blank=True, null=True)
  description = models.TextField(blank=True, null=True)
  grades = models.ManyToManyField(Grade)

  def __unicode__(self):
    return self.name

"""
Standards

"""
class Standard(models.Model):
  name = models.CharField(max_length=255)
  shortcode = models.CharField(max_length=50)
  description = models.TextField(blank=True, null=True)
  gradeband = models.ForeignKey(GradeBand)
  category = models.ForeignKey(Category)
  framework = models.ForeignKey(Framework, blank=True, null=True)
  slug = models.CharField(max_length=50, blank=True, null=True)

  def __unicode__(self):
    return self.framework.slug + ' ' + self.slug

  class Meta:
    ordering = ["shortcode"]

  def save(self, *args, **kwargs):
    self.framework = self.get_framework()
    self.slug = self.get_slug()
    super(Standard, self).save(*args, **kwargs)

  def get_framework(self):
    category = self.category
    while not hasattr(category, 'framework'):
      category = category.category
    return category.framework

  def get_slug(self):
    if self.framework.slug == 'CSTA':
      return self.category.shortcode + '.' + self.gradeband.shortcode + ':' + self.shortcode
    else:
      return self.framework.slug + '-' + self.shortcode


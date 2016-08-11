from django.db import models
from mezzanine.pages.models import Page, RichText

"""
Programming Environments

"""

class IDE(Page, RichText):
  url = models.URLField()

  def __unicode__(self):
    return self.title

  def get_absolute_url(self):
    return '/documentation/%s/' % self.slug


"""
Individual Code Elements

"""
class Block(Page, RichText):
  code = models.CharField('code', max_length=255)
  IDE = models.ForeignKey(IDE, blank=True, null=True)

  def __unicode__(self):
    return self.title

  def get_absolute_url(self):
    return '/documentation/%s/%s/' %(self.IDE.slug, self.slug)

  def get_IDE(self):
    parent = self.parent
    if hasattr(parent, 'ide'):
      return parent.ide

  def save(self, *args, **kwargs):
    self.IDE = self.get_IDE()
    super(Block, self).save(*args, **kwargs)

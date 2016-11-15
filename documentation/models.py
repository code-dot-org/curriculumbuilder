from django.db import models
from django.utils.text import slugify
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

    class Meta:
        ordering = ["IDE", "title"]

    def __unicode__(self):
        return self.block_with_ide

    @property
    def block_with_ide(self):
        return "%s - %s" % (self.IDE, self.title)

    def get_absolute_url(self):
        return '/documentation/%s/%s/' % (self.IDE.slug, self.slug)

    def get_IDE(self):
        parent = self.parent
        if hasattr(parent, 'ide'):
            return parent.ide

    def set_parent(self, new_parent):
        """
        Change the parent of this page, changing this page's slug to match
        the new parent if necessary.
        """

        # Make sure setting the new parent won't cause a cycle.
        parent = new_parent
        while parent is not None:
            if parent.pk == self.pk:
                raise AttributeError("You can't set a page or its child as"
                                     " a parent.")
            parent = parent.parent

        self.parent = new_parent
        self.save()

    def save(self, *args, **kwargs):
        self.IDE = self.get_IDE()
        if not self.slug:
            self.slug = slugify(self.title)
        super(Block, self).save(*args, **kwargs)


IDE._meta.get_field('slug').verbose_name = 'Slug'
Block._meta.get_field('slug').verbose_name = 'Slug'

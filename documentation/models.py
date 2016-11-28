import re

from django.db import models
from django.utils.text import slugify
from mezzanine.pages.models import Page, RichText, Orderable
from mezzanine.core.fields import RichTextField


"""
Programming Environments

"""


class IDE(Page, RichText):
    url = models.URLField()
    language = models.CharField(blank=True, null=True, max_length=64)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/documentation/%s/' % self.slug


"""
Toolbox Categories

"""


class Category(Orderable):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    IDE = models.ForeignKey(IDE)

    class Meta:
        ordering = ["IDE", "_order"]

    def __unicode__(self):
        return "%s: %s" % (self.IDE.title, self.name)


"""
Individual Code Elements

"""


class Block(Page, RichText):
    IDE = models.ForeignKey(IDE, blank=True, null=True)
    syntax = RichTextField(blank=True, null=True)
    ext_doc = models.URLField('External Documentation', blank=True, null=True,
                              help_text='Link to external documentation')
    proxy = models.ForeignKey("self",blank=True, null=True, help_text='Existing block to pull documentation from')
    signature = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    return_value = models.CharField(max_length=255, blank=True, null=True,
                                    help_text='Description of return value or alternate functionality')
    tips = RichTextField(blank=True, null=True, help_text='List of tips for using this block')
    video = models.ForeignKey('lessons.Resource', blank=True, null=True)
    _old_slug = models.CharField('old_slug', max_length=2000, blank=True, null=True)

    class Meta:
        ordering = ["IDE", "category"]

    def __unicode__(self):
        return self.block_with_ide

    @property
    def block_with_ide(self):
        return "%s - %s" % (self.IDE, self.title)

    @property
    def lessons_introduced(self):
        return self.lesson_set.filter(unit__login_required=False, curriculum__login_required=False)

    @property
    def code(self):
        if self.syntax:
            return self.syntax
        else:
            return self.title

    def get_absolute_url(self):
        return '/documentation/%s/%s/' % (self.IDE.slug, self.slug)

    def get_IDE(self):
        parent = self.parent
        if parent.content_model == 'ide':
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
                raise AttributeError("You can't set a page or its child as a parent.")
            parent = parent.parent

        self.parent = new_parent
        self.save()

    def save(self, *args, **kwargs):
        self.IDE = self.get_IDE()
        if not self.slug:
            self.slug = slugify(self.title)
        super(Block, self).save(*args, **kwargs)


"""
Parameters

"""


class Parameter(Orderable):
    name = models.CharField(max_length=255)
    block = models.ForeignKey(Block)
    type = models.CharField(max_length=64, blank=True, null=True, help_text='Data type, capitalized')
    required = models.BooleanField(default=True)
    description = RichTextField()

    def __unicode__(self):
        return self.name


"""
Code Examples

"""


class Example(Orderable):
    name = models.CharField(max_length=255, blank=True, null=True)
    block = models.ForeignKey(Block)
    description = models.TextField(blank=True, null=True)
    code = RichTextField()
    app = models.URLField(blank=True, null=True, help_text='Sharing link for example app')

    def __unicode__(self):
        return self.name

    def get_embed_app(self):
        if self.app:
            re_url = '\w*(studio.code.org\/p\w*\/\w+\/\w+)'
            if re.search(re_url, self.app):
                embed_code = 'https://%s/embed' % re.search(re_url, self.app).group(0)
                return embed_code
            else:
                return
        else:
            return


IDE._meta.get_field('slug').verbose_name = 'Slug'
Block._meta.get_field('slug').verbose_name = 'Slug'

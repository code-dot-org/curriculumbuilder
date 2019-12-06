import re
import logging
import json
import itertools

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from mezzanine.pages.models import Page, RichText, Orderable
from mezzanine.core.fields import RichTextField

from django_cloneable import CloneableMixin

from django_slack import slack_message

from jackfrost.receivers import build_page_for_obj

logger = logging.getLogger(__name__)


"""
Programming Environments

"""


class IDE(Page, RichText, CloneableMixin):
    url = models.URLField()
    language = models.CharField(blank=True, null=True, max_length=64)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/%s/' % self.slug

    def get_published_url(self):
        return '//docs.code.org/%s/' % self.slug

    def jackfrost_urls(self):
        urls = ["/documentation%s" % self.get_absolute_url()]
        return urls

    def jackfrost_can_build(self):
        return settings.ENABLE_PUBLISH and self.status == 2 and not self.login_required

    def publish(self, children=False, silent=False):
        if children:
            for block in self.blocks.all():
                for result in block.publish():
                    yield result
        if self.jackfrost_can_build():
            try:
                read, written = build_page_for_obj(IDE, self)
                if not silent:
                    slack_message('slack/message.slack', {
                        'message': 'published %s %s' % (self.content_model, self.title),
                        'color': '#00adbc'
                    })
                yield json.dumps(written)
                yield '\n'
            except Exception, e:
                yield json.dumps(e.message)
                yield '\n'
                logger.exception('Failed to publish %s' % self)

    def clone(self, attrs={}, commit=True, m2m_clone_reverse=True, exclude=[], children=False):

        # If new title and/or slug weren't passed, update
        attrs['title'] = attrs.get('title', "%s (clone)" % self.title)
        attrs['slug'] = attrs.get('slug', "%s_clone" % self.slug)

        # These must be excluded to avoid errors
        exclusions = ['children', 'blocks']
        exclude = exclude + list(set(exclusions) - set(exclude))

        # Check for slug uniqueness, if not unique append number
        for x in itertools.count(1, 100):
            if not IDE.objects.filter(slug=attrs['slug']):
                break
            attrs['slug'] = '%s-%d' % (attrs['slug'][:250], x)

        duplicate = super(IDE, self).clone(attrs=attrs, commit=commit,
                                           m2m_clone_reverse=m2m_clone_reverse, exclude=exclude)
        if children:
            for block in self.blocks.all():
                parent_cat = duplicate.categories.get(name=block.parent_cat.name)
                block.clone(attrs={'title': block.title, 'slug': block.slug, 'parent': duplicate.page_ptr,
                                   'parent_ide': duplicate, 'parent_cat': parent_cat},
                            exclude=['children', 'blocks'], children=True)
        return duplicate


"""
Toolbox Categories

"""


class Category(Orderable):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    parent_ide = models.ForeignKey(IDE, related_name='categories')

    class Meta:
        ordering = ["parent_ide", "_order"]

    def __unicode__(self):
        return "%s: %s" % (self.parent_ide.title, self.name)


"""
Individual Code Elements

"""


class Block(Page, RichText, CloneableMixin):
    parent_ide = models.ForeignKey(IDE, blank=True, null=True, related_name='blocks')
    syntax = RichTextField(blank=True, null=True)
    ext_doc = models.URLField('External Documentation', blank=True, null=True,
                              help_text='Link to external documentation')
    parent_object = models.ForeignKey("self", related_name='properties', blank=True, null=True,
                                      help_text='Parent object for property or method')
    proxy = models.ForeignKey("self", related_name="proxied", blank=True, null=True, on_delete=models.SET_NULL,
                              help_text='Existing block to pull documentation from')
    signature = models.CharField(max_length=255, blank=True, null=True)
    parent_cat = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL, related_name='blocks')
    return_value = models.CharField(max_length=255, blank=True, null=True,
                                    help_text='Description of return value or alternate functionality')
    tips = RichTextField(blank=True, null=True, help_text='List of tips for using this block')
    video = models.ForeignKey('lessons.Resource', blank=True, null=True, on_delete=models.SET_NULL,
                              related_name='blocks')
    # Using FileField instead of ImageField to support SVG blocks. ImageField is raster only :(
    image = models.FileField(blank=True, null=True, upload_to="blocks/")
    _old_slug = models.CharField('old_slug', max_length=2000, blank=True, null=True)

    def __unicode__(self):
        return self.block_with_ide

    @property
    def block_with_ide(self):
        return "%s - %s" % (self.parent_ide, self.title)

    @property
    def lessons_introduced(self):
        return self.lessons.filter(unit__login_required=False, curriculum__login_required=False,
                                   curriculum__version=0).order_by('curriculum', 'unit', 'number')

    @property
    def code(self):
        if self.syntax:
            return self.syntax
        else:
            return self.title

    def get_absolute_url(self):
        return '/%s/%s/' % (self.parent_ide.slug, self.slug)

    def get_published_url(self):
        return '//docs.code.org/%s/%s/' % (self.parent_ide.slug, self.slug)

    def jackfrost_urls(self):
        urls = ["/documentation%s" % self.get_absolute_url(), "/documentation%sembed/" % self.get_absolute_url()]
        return urls

    def jackfrost_can_build(self):
        return settings.ENABLE_PUBLISH and self.status == 2 and not self.login_required

    def publish(self, children=False, silent=False):
        if self.jackfrost_can_build():
            try:
                read, written = build_page_for_obj(Block, self)
                if not silent:
                    slack_message('slack/message.slack', {
                        'message': 'published %s %s' % (self.content_model, self.title),
                        'color': '#00adbc'
                    })
                yield json.dumps(written)
                yield '\n'
            except Exception, e:
                yield json.dumps(e.message)
                yield '\n'
                logger.exception('Failed to publish %s' % self)

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
        self.parent = Page.objects.get(pk=self.parent_id)
        self.parent_ide = self.get_IDE()
        if not self.slug:
            self.slug = slugify(self.title)
        super(Block, self).save(*args, **kwargs)

    def clone(self, attrs={}, commit=True, m2m_clone_reverse=True, exclude=[], children=False):

        # If new title and/or slug weren't passed, update
        attrs['title'] = attrs.get('title', "%s (clone)" % self.title)
        attrs['slug'] = attrs.get('slug', "%s_clone" % self.slug)

        # These must be excluded to avoid errors
        exclusions = ['lessons', 'proxied', 'properties']
        exclude = exclude + list(set(exclusions) - set(exclude))

        if not attrs.get('slug', False):
            # If block is copied within existing IDE, check for slug uniqueness
            parent_ide = attrs.get('parent_ide', self.parent_ide)
            for x in itertools.count(1, 100):
                if not Block.objects.filter(slug=attrs['slug'], parent_ide=parent_ide):
                    break
                attrs['slug'] = '%s-%d' % (attrs['slug'][:250], x)

        duplicate = super(Block, self).clone(attrs=attrs, commit=commit,
                                             m2m_clone_reverse=m2m_clone_reverse, exclude=exclude)

        # Keywords are a complex model and don't survive cloning, so we re-add here before returning the clone
        if self.keywords.count() > 0:
            keyword_ids = self.keywords.values_list('keyword__id', flat=True)
            for keyword_id in keyword_ids:
                duplicate.keywords.create(keyword_id=keyword_id)
            duplicate.keywords_string = self.keywords_string
        duplicate.save()

        return duplicate


"""
Parameters

"""


class Parameter(Orderable, CloneableMixin):
    name = models.CharField(max_length=255)
    parent_block = models.ForeignKey(Block, related_name='parameters')
    type = models.CharField(max_length=64, blank=True, null=True, help_text='Data type, capitalized')
    required = models.BooleanField(default=True)
    description = RichTextField()

    def __unicode__(self):
        return self.name


"""
Code Examples

"""


class Example(Orderable, CloneableMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    parent_block = models.ForeignKey(Block, related_name='examples')
    description = models.TextField(blank=True, null=True)
    code = RichTextField()
    app = models.URLField(blank=True, null=True, help_text='Sharing link for example app')
    image = models.ImageField(blank=True, null=True)

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


"""
Content Maps

"""


class Map(Page, RichText, CloneableMixin):
    blocks = models.ManyToManyField(Block, blank=True)

    def __unicode__(self):
        return self.title

    # Override default Page override logic so that new slugs get generated on move
    def overridden(self):
        return False

    # Returns Map instead of Page so that we can use get_absolute_url to get the correct link
    def get_children(self):
        return Map.objects.filter(parent=self).all()

    def get_absolute_url_for_curriculum_code_org_map_menu(self):
        return '/documentation/%s/' % self.slug

    def get_absolute_url_for_studio_code_org_map_menu(self):
        return '/docs/%s/' % self.slug

    def get_published_url(self):
        return '//docs.code.org%s' % self.get_absolute_url()

    def jackfrost_urls(self):
        urls = ["/documentation%s" % self.get_absolute_url()]
        return urls

    def jackfrost_can_build(self):
        return settings.ENABLE_PUBLISH and self.status == 2 and not self.login_required

    def publish(self, children=False, silent=False):
        if children:
            for page in self.children.all():
                for result in page.map.publish(children=children):
                    yield result
        if self.jackfrost_can_build():
            try:
                read, written = build_page_for_obj(Map, self)
                if not silent:
                    slack_message('slack/message.slack', {
                        'message': 'published %s %s' % (self.content_model, self.title),
                        'color': '#00adbc'
                    })
                yield json.dumps(written)
                yield '\n'
            except Exception, e:
                yield json.dumps(e.message)
                yield '\n'
                logger.exception('Failed to publish %s' % self)

    def clone(self, attrs={}, commit=True, m2m_clone_reverse=True, exclude=[], children=False):

        # If new title and/or slug weren't passed, update
        attrs['title'] = attrs.get('title', "%s (clone)" % self.title)
        attrs['slug'] = attrs.get('slug', "%s_clone" % self.slug)

        if not attrs.get('slug', False):
            # If block is copied within existing IDE, check for slug uniqueness
            parent = attrs.get('parent', self.parent)

            for x in itertools.count(1, 100):
                if not Map.objects.filter(slug=attrs['slug'], parent=parent):
                    break
                attrs['slug'] = '%s-%d' % (attrs['slug'][:250], x)

        duplicate = super(Map, self).clone(attrs=attrs, commit=commit,
                                           m2m_clone_reverse=m2m_clone_reverse, exclude=exclude)

        # Keywords are a complex model and don't survive cloning, so we re-add here before returning the clone
        if self.keywords.count() > 0:
            keyword_ids = self.keywords.values_list('keyword__id', flat=True)
            for keyword_id in keyword_ids:
                duplicate.keywords.create(keyword_id=keyword_id)
            duplicate.keywords_string = self.keywords_string
        duplicate.save()

        return duplicate


IDE._meta.get_field('slug').verbose_name = 'Slug'
Block._meta.get_field('slug').verbose_name = 'Slug'
Map._meta.get_field('slug').verbose_name = 'Slug'

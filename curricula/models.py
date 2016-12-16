import re
import logging
import json

from django.conf import settings
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from mezzanine.pages.models import Page, RichText, Orderable, PageMoveException
from mezzanine.core.fields import RichTextField

from jackfrost.utils import build_page_for_obj
from jackfrost.tasks import build_single

from django_slack import slack_message

from standards.models import Standard, GradeBand, Category, Framework
import lessons.models

logger = logging.getLogger(__name__)

"""
Curriculum

"""


class Curriculum(Page, RichText):
    gradeband = models.ForeignKey(GradeBand)
    frameworks = models.ManyToManyField(Framework, blank=True, help_text='Standards frameworks aligned to')
    unit_numbering = models.BooleanField(default=True)
    auto_forum = models.BooleanField(default=False, help_text='Automatically generate forum links?')
    display_questions = models.BooleanField(default=False, help_text='Display open questions and feedback form?')
    feedback_url = models.URLField(blank=True, null=True, help_text='URL to feedback form, using % operators')
    feedback_vars = models.CharField(max_length=255, blank=True, null=True,
                                     help_text='Tuple of properties to use in feedback url')

    class Meta:
        verbose_name_plural = "curricula"

    def __unicode__(self):
        return self.title

    def can_move(self, request, new_parent):
        if new_parent is not None:
            msg = 'Curriculum must be a top level object'
            raise PageMoveException(msg)

    def get_absolute_url(self):
        return '/%s/' % self.slug

    def get_pdf_url(self):
        return '/%s.pdf' % self.slug

    def get_standards_url(self):
        return '%sstandards/' % self.get_absolute_url()

    def get_resources_url(self):
        return '%sresources/' % (self.get_absolute_url())

    def get_blocks_url(self):
        return '%scode/' % (self.get_absolute_url())

    def get_vocab_url(self):
        return '%svocab/' % (self.get_absolute_url())

    # Return publishable urls for JackFrost
    def jackfrost_urls(self):
        urls = [self.get_absolute_url(), self.get_standards_url(), self.get_resources_url(),
                self.get_blocks_url(), self.get_vocab_url()]
        return urls

    def jackfrost_can_build(self):
        return settings.ENABLE_PUBLISH and self.status == 2 and not self.login_required

    def publish(self, children=False):
        if children:
            for unit in self.units:
                for result in unit.publish(True):
                    yield result
        if self.jackfrost_can_build():
            try:
                read, written = build_page_for_obj(Curriculum, self)
                attachments = [
                    {
                        'color': '#00adbc',
                        'title': 'URL',
                        'text': self.get_absolute_url(),
                    },
                    {
                        'color': '#00adbc',
                        'title': 'Publishing Details',
                        'text': json.dumps(written),
                    },
                ]

                slack_message('slack/message.slack', {
                    'message': 'published %s %s' % (self.content_model, self.title),
                }, attachments)
                yield '%s\n' % written
            except Exception, e:
                yield 'ERROR\n%s\n' % e.message
                logger.exception('Failed to publish %s' % self)

    def publish_pdfs(self, *args):
        if self.jackfrost_can_build():
            try:
                read, written = build_single(self.get_pdf_url())
                attachments = [
                    {
                        'color': '#00adbc',
                        'title': 'URL',
                        'text': self.get_pdf_url(),
                    },
                    {
                        'color': '#00adbc',
                        'title': 'PDF Publishing Details',
                        'text': json.dumps(written),
                    },
                ]

                slack_message('slack/message.slack', {
                    'message': 'published %s %s' % (self.content_model, self.title),
                }, attachments)
                yield '%s\n' % written
            except Exception, e:
                yield 'ERROR\n%s\n' % e.message
                logger.exception('Failed to publish PDF for %s' % self)

    @property
    def units(self):
        return Unit.objects.filter(parent=self)


"""
Curricular Unit

"""


class Unit(Page, RichText):
    curriculum = models.ForeignKey(Curriculum, blank=True, null=True)
    number = models.IntegerField('Number', blank=True, null=True)
    stage_name = models.CharField('Script', max_length=255, blank=True, null=True, help_text='Name of Code Studio script')

    def __unicode__(self):
        return self.title

    def can_move(self, request, new_parent):
        parent_type = getattr(new_parent, 'content_model', None)
        if not parent_type == 'curriculum':
            msg = 'Unit must live directly under a curriculum'
            raise PageMoveException(msg)

    def get_absolute_url(self):
        return '%s%s/' % (self.curriculum.get_absolute_url(), self.slug)

    def get_compiled_url(self):
        return '%s%s/compiled/' % (self.curriculum.get_absolute_url(), self.slug)

    def get_pdf_url(self):
        return '%s%s.pdf' % (self.curriculum.get_absolute_url(), self.slug)

    def get_resources_pdf_url(self):
        return '%s%s_resources.pdf' % (self.curriculum.get_absolute_url(), self.slug)

    def get_resources_url(self):
        return '%sresources/' % (self.get_absolute_url())

    def get_blocks_url(self):
        return '%scode/' % (self.get_absolute_url())

    def get_vocab_url(self):
        return '%svocab/' % (self.get_absolute_url())

    def get_standards_url(self):
        return '%sstandards/' % (self.get_absolute_url())

    def get_number(self):
        return int(self._order) + 1

    def get_unit_numbering(self):
        if self.curriculum.unit_numbering:
            return "Unit %d" % self.number
        else:
            return

    # Return publishable urls for JackFrost
    def jackfrost_urls(self):
        urls = [self.get_absolute_url(), self.get_resources_url(), self.get_blocks_url(),
                self.get_vocab_url(), self.get_standards_url(), self.get_compiled_url()]
        # urls.append(self.get_pdf_url())
        # urls.append(self.get_resources_pdf_url())
        return urls

    def pdf_urls(self):
        return [self.get_pdf_url(), self.get_resources_pdf_url()]

    def jackfrost_can_build(self):
        return settings.ENABLE_PUBLISH and self.status == 2 and not self.login_required and not self.curriculum.login_required

    def publish(self, children=False):
        if children:
            for lesson in self.lesson_set.all():
                try:
                    for result in lesson.publish():
                        yield result
                except Exception, e:
                    yield 'ERROR\n%s\n' % e.message
                    logger.exception('Failed to publish %s' % lesson)
        if self.jackfrost_can_build():
            try:
                read, written = build_page_for_obj(Unit, self)
                attachments = [
                    {
                        'color': '#00adbc',
                        'title': 'URL',
                        'text': self.get_absolute_url(),
                    },
                    {
                        'color': '#00adbc',
                        'title': 'Publishing Details',
                        'text': json.dumps(written),
                    },
                ]

                slack_message('slack/message.slack', {
                    'message': 'published %s %s' % (self.content_model, self.title),
                }, attachments)
                yield '%s\n' % written
            except Exception, e:
                yield 'ERROR\n%s\n' % e.message
                logger.exception('Failed to publish %s' % self)

    def publish_pdfs(self, *args):
        if self.jackfrost_can_build():
            for url in self.pdf_urls():
                try:
                    read, written = build_single(url)
                    attachments = [
                        {
                            'color': '#00adbc',
                            'title': 'URL',
                            'text': url,
                        },
                        {
                            'color': '#00adbc',
                            'title': 'PDF Publishing Details',
                            'text': json.dumps(written),
                        },
                    ]

                    slack_message('slack/message.slack', {
                        'message': 'published PDF for %s %s' % (self.content_model, self.title),
                    }, attachments)
                    yield '%s\n' % written
                except Exception, e:
                    yield 'ERROR\n%s\n' % e.message
                    logger.exception('Failed to publish PDF %s' % self)

    # Eventually this will need to address naming differences between CSF and CSD/CSP
    @property
    def short_name(self):
        if self.curriculum.unit_numbering:
            return self.get_unit_numbering()
        else:
            return self.title

    @property
    def long_name(self):
        if self.curriculum.unit_numbering:
            return "%s - %s" % (self.get_unit_numbering(), self.title)
        else:
            return self.title

    @property
    def header_corner(self):
        if self.curriculum.unit_numbering:
            return "<span class='h2'>Unit</span><span class='h1'>%d</span>" % self.number
        else:
            re_title = "(\w+) (\w+)"
            re_match = re.search(re_title, self.title)
            return "<span class='h2'>%s</span><span class='h1'>%s</span>" % (re_match.group(1), re_match.group(2))

    @property
    def block_count(self):
        num_blocks = self.lessons.aggregate(Count('blocks'))
        return num_blocks.get('blocks__count')

    @property
    def vocab_count(self):
        num_blocks = self.lessons.aggregate(Count('vocab'))
        return num_blocks.get('vocab__count')

    @property
    def lessons(self):
        # Exclude optional lessons by default, they'll only show up if explicitly called from a parent lesson
        return self.lesson_set.all().exclude(keywords__keyword__title="Optional")

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

        if not self.stage_name:
            self.stage_name = "%s%d" % (self.curriculum.slug, self.number)

        super(Unit, self).save(*args, **kwargs)


"""
Unit Chapter

"""


class Chapter(Page, RichText):
    number = models.IntegerField('Number', blank=True, null=True)
    questions = RichTextField(blank=True, null=True, help_text="md list of big questions")
    understandings = models.ManyToManyField(Category, blank=True)
    _old_slug = models.CharField('old_slug', max_length=2000, blank=True, null=True)

    class Meta:
        order_with_respect_to = "parent"

    def __unicode__(self):
        return self.title

    def can_move(self, request, new_parent):
        parent_type = getattr(new_parent, 'content_model', None)
        if not parent_type == 'unit':
            msg = 'Chapter must live directly under a unit'
            raise PageMoveException(msg)

    def get_absolute_url(self):
        return "%sch%s/" % (self.unit.get_absolute_url(), str(self.number))

    def get_number(self):
        return int(self._order) + 1

    def jackfrost_can_build(self):
        return settings.ENABLE_PUBLISH and self.status == 2 and not self.login_required

    @property
    def unit(self):
        return self.parent.unit

    @property
    def curriculum(self):
        return self.unit.curriculum

    @property
    def lessons(self):
        return lessons.models.Lesson.objects.filter(parent__chapter=self, login_required=False)

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
    if settings.AUTO_PUBLISH and instance.jackfrost_can_build():
        build_single.delay(instance.get_absolute_url())


@receiver(post_save, sender=Unit)
def unit_handler(sender, instance, **kwargs):
    if settings.AUTO_PUBLISH and instance.jackfrost_can_build():
        for url in instance.jackfrost_urls():
            build_single.delay(url)
            instance.curriculum.save()


@receiver(post_save, sender=Chapter)
def chapter_handler(sender, instance, **kwargs):
    if settings.AUTO_PUBLISH and instance.jackfrost_can_build():
        build_single.delay(instance.get_absolute_url())

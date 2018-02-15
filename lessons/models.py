import re
import itertools
import datetime
import urllib2
import logging
import json
from urlparse import urlparse
# from copy import copy, deepcopy
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.auth.models import User

from mezzanine.pages.models import Page, RichText, Orderable, PageMoveException
from mezzanine.core.fields import RichTextField
from mezzanine.generic.fields import CommentsField, KeywordsField
from sortedm2m.fields import SortedManyToManyField
from jackfrost.tasks import build_single
from jsonfield import JSONField
from standards.models import Standard
from documentation.models import Block
from django_slack import slack_message

from curriculumBuilder import settings

from django_cloneable import CloneableMixin

import reversion
from reversion.models import Version

import curricula.models

logger = logging.getLogger(__name__)

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
            return "%s (math): %s" % (self.word, self.simpleDef)
        else:
            return "%s: %s" % (self.word, self.simpleDef)

    def save(self, *args, **kwargs):
        if not self.detailDef:
            self.detailDef = self.simpleDef
        super(Vocab, self).save(*args, **kwargs)


"""
Linked Resources

"""


class Resource(Orderable):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    student = models.BooleanField('Student Facing', default=False)
    gd = models.BooleanField('Google Doc', default=False)
    url = models.URLField(blank=True, null=True)
    dl_url = models.URLField('Download URL', help_text='Alternate download url', blank=True, null=True)
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        ordering = ['name', ]

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
        if self.type:
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

        # Moving this to the template to allow for more formatting
        # elif self.gd:
        #     formatted = "%s (<a href='%s' class='print_link'>PDF</a> | <a href='%s' class='print_link'>DOCX</a> | " \
        #                 "<a href='%s' class='print_link'>copy Gdoc</a>)" \
        #                 % (formatted, self.gd_pdf(), self.gd_doc(), self.gd_copy())
        return formatted

    def formatted_student(self):
        if self.url:
            if self.gd:
                formatted = "<a href='%s' target='_blank'>%s</a>" % (self.gd_pdf(), self.name)
            else:
                formatted = "<a href='%s' target='_blank'>%s</a>" % (self.fallback_url(), self.name)
        else:
            formatted = self.name
        if self.type:
            formatted = "%s - %s" % (formatted, self.type)
        if self.dl_url:
            formatted = "%s (<a href='%s' class='print_link'>download</a>)" % (formatted, self.dl_url)
        return formatted

    def formatted_md(self):
        if self.url:
            if self.gd:
                formatted = "[%s](%s)" % (self.name, self.gd_pdf())
            else:
                formatted = "[%s](%s)" % (self.name, self.fallback_url())
        else:
            formatted = self.name
        if self.type:
            formatted = "%s - %s" % (formatted, self.type)
        if self.dl_url:
            formatted = "%s ([download](%s))" % (formatted, self.dl_url)
        elif self.gd:
            formatted = "%s (copy as [MS Word](%s), [Google Doc](%s))" \
                        % (formatted, self.gd_doc(), self.gd_copy())

        return formatted

    # If resource lives on pegasus check to see if it's on prod, otherwise fallback to staging
    def fallback_url(self):
        parsed = urlparse(self.url)
        if parsed.netloc == 'code.org':
            try:
                urllib2.urlopen(parsed.geturl())
                return self.url
            except:
                return '%s://staging.%s%s' % (parsed.scheme, parsed.netloc, parsed.path)
        else:
            return self.url

    def md_tag(self):
        if self.slug:
            return '[r ' + self.slug + ']'
        else:
            return '[r ' + self.name + ']'

    def gd_pdf(self):
        try:
            re_doc = '(drive|docs)\.google\.com\/(a\/code.org\/)?(document\/d\/|open\?id\=)(?P<doc_id>[\w-]*)'
            doc_id = re.search(re_doc, self.url).group('doc_id')
            pdf = 'https://docs.google.com/document/d/%s/export?format=pdf' % doc_id
            return pdf
        except:
            return self.url

    def gd_doc(self):
        try:
            re_doc = '(drive|docs)\.google\.com\/(a\/code.org\/)?(document\/d\/|open\?id\=)(?P<doc_id>[\w-]*)'
            doc_id = re.search(re_doc, self.url).group('doc_id')
            pdf = 'https://docs.google.com/document/d/%s/export?format=doc' % doc_id
            return pdf
        except:
            return self.url

    def gd_copy(self):
        try:
            re_doc = '(drive|docs)\.google\.com\/(a\/code.org\/)?(document\/d\/|open\?id\=)(?P<doc_id>[\w-]*)'
            doc_id = re.search(re_doc, self.url).group('doc_id')
            pdf = 'https://docs.google.com/document/d/%s/copy' % doc_id
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


class Lesson(Page, RichText, CloneableMixin):
    overview = RichTextField('Lesson Overview')
    duration = models.CharField('Duration', help_text='Duration of lesson',
                                max_length=255, blank=True, null=True)
    week = models.IntegerField('Week', help_text='Week within the unit (only use for first lesson of the week)',
                               blank=True, null=True)
    pacing_weight = models.DecimalField('Pacing Weight', help_text='Higher numbers take up more space pacing calendar',
                                        default=1, max_digits=4, decimal_places=1, blank=True, null=True)
    unplugged = models.BooleanField(default=False)
    resources = SortedManyToManyField(Resource, blank=True)
    prep = RichTextField('Preparation', help_text='ToDos for the teacher to prep this lesson', blank=True, null=True)
    questions = RichTextField('Support Details', help_text='Open questions or comments about this lesson',
                              blank=True, null=True)
    cs_content = RichTextField('Purpose', help_text='Purpose of this lesson in progression and CS in general',
                               blank=True, null=True)
    ancestor = models.ForeignKey('self', blank=True, null=True)
    standards = models.ManyToManyField(Standard, blank=True)
    anchor_standards = models.ManyToManyField(Standard, help_text='1 - 3 key standards this lesson focuses on',
                                              related_name="anchors", blank=True)
    vocab = models.ManyToManyField(Vocab, blank=True)
    blocks = models.ManyToManyField(Block, blank=True, related_name='lessons')
    comments = CommentsField()
    unit = models.ForeignKey(curricula.models.Unit, blank=True, null=True)
    curriculum = models.ForeignKey(curricula.models.Curriculum, blank=True, null=True)
    number = models.IntegerField('Number', blank=True, null=True)
    image = models.ImageField('Image', blank=True, null=True)
    stage = JSONField('Code Studio stage', blank=True, null=True)
    _old_slug = models.CharField('old_slug', max_length=2000, blank=True, null=True)

    class Meta:
        ordering = ["number"]

    def __unicode__(self):
        return self.title

    def can_move(self, request, new_parent):
        parent_type = getattr(new_parent, 'content_model', None)
        if not (parent_type == 'lesson' or parent_type == 'chapter' or parent_type == 'unit'):
            print "no unit here"
            msg = 'Lesson cannot live under a %s' % parent_type
            raise PageMoveException(msg)

    def get_absolute_url(self):
        # Check if this is the child of a lesson, and therefore optional
        if hasattr(self.parent, 'lesson'):
            return "%soptional/%s/" % (self.parent.lesson.get_absolute_url(), str(self.number))
        try:
            return "%s%s/" % (self.unit.get_absolute_url(), str(self.number))
        except AttributeError:
            return "%s%s/" % (self.get_unit().get_absolute_url(), str(self.number))

    def get_overview_url(self):
        return '%soverview/' % self.get_absolute_url()

    def get_unit(self):
        parent = self.parent
        while not parent.content_model == 'unit':
            parent = parent.parent
            if parent is None:
                return None
        return parent.unit

    '''
    def get_number(self):
        order = 1
        if self.parent.content_model == 'chapter':
            chapter = self.parent.chapter
            chapters = chapter.parent.unit.chapters
            while chapter is not None and chapter._order > 0:
                try:
                    chapter = chapters[chapter._order - 1]
                    if hasattr(chapter, "chapter"):
                        chapter = chapter.chapter
                        order += chapter.lessons.count()
                except AttributeError as e:
                    chapter = None

        if self._order is not None:
            try:
                order += int(self._order)
            except Exception as e:
                print(e)

        return order
    '''

    def get_number(self):
        order = 1
        if self.is_optional:
            peers = self.parent.lesson.optional_lessons.order_by('_order')
        else:
            peers = self.unit.lessons.all().order_by('parent___order', '_order')
        for lesson in peers:
            if lesson == self:
                break
            else:
                order += 1
        return order

    def get_curriculum(self):
        return self.get_unit().curriculum

    def get_levels(self):
        if self.stage:
            raw_levels = self.stage.get('levels')

            levels = []  # To store levels organized by logical chunk
            counter = 0
            last_type = raw_levels[0].get('named_level')
            last_progression = raw_levels[0].get('progression')
            levels.insert(counter, {'named': last_type, 'progression': last_progression, 'levels': []})

            for level in raw_levels:

                current_type = level.get('named_level')
                current_progression = level.get('progression')
                if last_type != current_type or last_progression != current_progression:
                    last_type = current_type
                    last_progression = current_progression
                    counter += 1
                    levels.insert(counter, {'named': last_type, 'progression': last_progression, 'levels': []})

                levels[counter]['levels'].append(level)

            return levels
        else:
            return

    def get_levels_from_levelbuilder(self):
        try:
            url = "https://levelbuilder-studio.code.org/s/%s/stage/%d/summary_for_lesson_plans" % (
            self.unit.stage_name, self.number)
            response = urllib2.urlopen(url)
            data = json.loads(response.read())
            self.stage = data
            self.save()
        except Exception:
            logger.warning("Couldn't get stage details for %s" % self)

    # Return publishable urls for JackFrost
    def jackfrost_urls(self):
        urls = [self.get_absolute_url(), self.get_overview_url()]
        return urls

    def jackfrost_can_build(self):
        try:
            can_build = settings.ENABLE_PUBLISH and self.status == 2 and not self.login_required and \
                        not self.unit.login_required and not self.curriculum.login_required
        except:
            can_build = False

        return can_build

    def publish(self, children=False):
        if self.jackfrost_can_build():
            for url in self.jackfrost_urls():
                try:
                    read, written = build_single(url)
                    slack_message('slack/message.slack', {
                        'message': 'published %s %s' % (self.content_model, self.title),
                        'color': '#00adbc'
                    })
                    yield json.dumps(written)
                    yield '\n'
                except Exception, e:
                    yield json.dumps(e.message)
                    yield '\n'
                    logger.exception('Failed to publish %s' % url)
        else:
            fail_msg = 'Attempted to publish %s %s lesson %s, ' \
                       'but it is not publishable.' % (self.curriculum.slug, self.unit.slug, self.number)
            slack_message('slack/message.slack', {
                'message': fail_msg
            })
            yield '%s\n' % fail_msg

    def save(self, *args, **kwargs):
        self.parent = Page.objects.get(pk=self.parent_id)
        try:
            self.unit = self.get_unit()
        except Exception:
            logger.exception("Couldn't get unit for %s" % self)
        try:
            self.curriculum = self.get_curriculum()
        except Exception:
            logger.exception("Couldn't get curriculum for %s" % self)
        try:
            self.number = self.get_number()
        except Exception as e:
            print(e)
            print("couldn't get number")
            logger.exception("Couldn't get number for %s" % self)

        '''
        # Don't try to get stage data on every save.
        try:
            url = "https://levelbuilder-studio.code.org/s/%s/stage/%d/summary_for_lesson_plans" % (
            self.unit.stage_name, self.number)
            response = urllib2.urlopen(url)
            data = json.loads(response.read())
            self.stage = data
        except Exception:
            logger.warning("Couldn't get stage details for %s" % self)
        '''

        super(Lesson, self).save(*args, **kwargs)

    def clone(self, attrs={}, commit=True, m2m_clone_reverse=True, exclude=[]):
        # If new title and/or slug weren't passed, update
        attrs['title'] = attrs.get('title', "%s (clone)" % self.title)

        # Add default values
        attrs['ancestor'] = self

        # These must be excluded to avoid errors
        exclusions = ['children', 'lesson_set', 'ancestor', 'keywords']
        exclude = exclude + list(set(exclusions) - set(exclude))

        duplicate = super(Lesson, self).clone(attrs=attrs, commit=commit,
                                              m2m_clone_reverse=m2m_clone_reverse, exclude=exclude)

        if self.optional_lessons.count() > 0:
            for lesson in self.optional_lessons.all():
                lesson.clone(attrs={'title': lesson.title, 'parent': duplicate.page_ptr, 'no_renumber': True})

        if not attrs.get('no_renumber', False):
            duplicate.unit.renumber_lessons()

        # Keywords are a complex model and don't survive cloning, so we re-add here before returning the clone
        if self.keywords.count() > 0:
            keyword_ids = self.keywords.values_list('keyword__id', flat=True)
            for keyword_id in keyword_ids:
                duplicate.keywords.create(keyword_id=keyword_id)
            duplicate.keywords_string = self.keywords_string
        duplicate.save()

        return duplicate

    @property
    def optional_lessons(self):
        return Lesson.objects.filter(parent__lesson=self)

    @property
    def chapter(self):
        parent = self.parent
        if hasattr(parent, 'chapter'):
            return parent.chapter
        else:
            return

    @property
    def is_optional(self):
        return self.parent.content_model == 'lesson'

    @property
    def forum_link(self):
        if self.is_optional:
            return "//forum.code.org/c/%s%d/optional%02d" % (self.curriculum.slug, self.unit.number, self.number)
        else:
            return "//forum.code.org/c/%s%d/lesson%02d" % (self.curriculum.slug, self.unit.number, self.number)

    @property
    def feedback_link(self):
        if self.curriculum.feedback_url:
            if self.curriculum.feedback_vars:
                replacements = eval(self.curriculum.feedback_vars)
                return self.curriculum.feedback_url % replacements
            else:
                return self.curriculum.feedback_url
        else:
            return

    @property
    def zendesk_link(self):
        message = "Bug in %s unit %s lesson %d curriculum.code.org%s" % (
        str(self.curriculum), self.unit.number, self.number, self.get_absolute_url())
        url = "https://support.code.org/hc/en-us/requests/new?description=%s" % urllib2.quote(message)
        return url

    @property
    def code_studio_link(self):
        return "https://studio.code.org/s/%s/stage/%d/puzzle/1/" % (
            self.unit.stage_name, self.number)

    @property
    def changelog(self):
        return Version.objects.get_for_object(self).filter(revision__user__username=settings.CHANGELOG_USER)

    @property
    def standards_by_category(self):
        results = {}
        for framework in self.curriculum.frameworks.all():
            results[framework.slug] = {}
            for category in framework.top_categories:
                results[framework.slug][category.shortcode] = []

        for standard in self.standards.all():
            results[standard.framework.slug][standard.top_category.shortcode].append(standard)


"""
Activities that compose a lesson

"""


class Activity(Orderable, CloneableMixin):
    name = models.CharField(max_length=255)
    content = RichTextField('Activity Content')
    keywords = KeywordsField()
    time = models.CharField(max_length=255, blank=True, null=True)
    lesson = models.ForeignKey(Lesson)
    ancestor = models.ForeignKey('self', blank=True, null=True)

    class Meta:
        verbose_name_plural = "activities"
        order_with_respect_to = "lesson"

    def __unicode__(self):
        if self.time:
            return "%s (%s)" % (self.name, self.time)
        return self.name

    def save(self, *args, **kwargs):
        try:
            old_activity = Activity.objects.get(pk=self.pk)
            if old_activity._order != self._order:
                logger.debug('Activity order changing! Activity %s, lesson %s' % (self.pk, self.lesson.pk))
        except:
            pass
        super(Activity, self).save(*args, **kwargs)


"""
Prerequisite Skills

"""


class Prereq(Orderable, CloneableMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    lesson = models.ForeignKey(Lesson)

    class Meta:
        order_with_respect_to = "lesson"

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.name
        super(Prereq, self).save(*args, **kwargs)


"""
Learning Objectives

"""


class Objective(Orderable, CloneableMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    lesson = models.ForeignKey(Lesson)

    class Meta:
        order_with_respect_to = "lesson"

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


Lesson._meta.get_field('login_required').verbose_name = 'Hidden'
Lesson._meta.get_field('login_required').help_text = "Hide from listings and prevent be publishing."
Lesson._meta.get_field('status').help_text = "With draft chosen this lesson will not be updated during publish."

reversion.register(Activity, follow=('lesson', ))
reversion.register(Objective, follow=('lesson', ))


@receiver(post_delete, sender=Lesson)
def reorder_peers(sender, instance, **kwargs):
    for lesson in instance.curriculum.lesson_set.all():
        Lesson.objects.filter(id=lesson.id).update(number=lesson.get_number())


"""
These post_save receivers call the JackFrost build command
to automatically publish lessons on save, as long as they
are marked publish (status == 2) and do not require a login to view.
We also kick off a save for the parent unit and chapter
if applicable to ensure listing pages are updated

"""

'''
@receiver(post_save, sender=Lesson)
def lesson_handler(sender, instance, **kwargs):
    new_number = instance.get_number()
    if instance.number != new_number:
        instance.number = new_number
        return
    if settings.AUTO_PUBLISH and instance.jackfrost_can_build():
        logger.debug("Attempting to publish lesson %s (pk %s)" % (instance.title, instance.pk))
        build_single.delay(instance.get_absolute_url())
        instance.unit.save()
        if hasattr(instance.parent, "chapter"):
            instance.parent.chapter.save()
    else:
        logger.debug("Couldn't publish lesson %s because settings %s and jackfrost build %s" % (
        instance.pk, settings.AUTO_PUBLISH, instance.jackfrost_can_build()))
'''

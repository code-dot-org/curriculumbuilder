import re
import itertools
import datetime
import urllib2
import logging
import json
import bleach
from urlparse import urlparse
# from copy import copy, deepcopy
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.contrib.auth.models import User

from mezzanine.pages.models import Page, RichText, Orderable, PageMoveException
from mezzanine.core.fields import RichTextField
from mezzanine.generic.fields import CommentsField, KeywordsField
from mezzanine.generic.models import Keyword as BaseKeyword
from sortedm2m.fields import SortedManyToManyField
from jackfrost.tasks import build_single
from jsonfield import JSONField
from standards.models import Standard
from documentation.models import Block
from django_slack import slack_message

from curriculumBuilder import settings
from i18n.models import Internationalizable, InternationalizablePage
from i18n.utils import I18nFileWrapper

from django_cloneable import CloneableMixin

import reversion
from reversion.models import Version

import curricula.models

logger = logging.getLogger(__name__)

RE_DOC = '(drive|docs)\.google\.com\/(a\/code.org\/)?(document\/d\/|open\?id\=)(?P<doc_id>[\w-]*)'

# Bleach settings for extracting html
allowed_tags = bleach.ALLOWED_TAGS + ['head', 'body', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p',
                                      'table', 'tr', 'td', 'pre']
allowed_attrs = bleach.ALLOWED_ATTRIBUTES
allowed_attrs['*'] = ['style', 'id', 'class', 'alt', 'src', 'width', 'height', 'type']
allowed_styles = ['background-color', 'color', 'font-family', 'font-size', 'font-style', 'font-width',
                  'strike-through', 'text-align', 'text-decoration']


"""
Keyword

"""


class Keyword(BaseKeyword, Internationalizable):

    class Meta:
        proxy = True

    @property
    def i18n_key(self):
        return self.get_slug()

    @classmethod
    def internationalizable_fields(cls):
        return ['title']

    @property
    def should_be_translated(self):
        return True


"""
Vocabulary

"""


class Vocab(Internationalizable):
    word = models.CharField(max_length=255)
    simpleDef = models.TextField()
    detailDef = models.TextField(blank=True, null=True)
    mathy = models.BooleanField(default=False)

    class Meta:
        ordering = ["word"]
        verbose_name_plural = "vocab words"
        unique_together = ('word', 'mathy')

    @property
    def i18n_key(self):
        return slugify(self.get_untranslated_field('word'))

    @classmethod
    def internationalizable_fields(cls):
        return ['word', 'simpleDef', 'detailDef']

    @property
    def should_be_translated(self):
        return not self.mathy and any(lesson.should_be_translated for lesson in self.lesson_set.all())

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


class Resource(Orderable, Internationalizable):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    student = models.BooleanField('Student Facing', default=False)
    gd = models.BooleanField('Google Doc', default=False)
    url = models.URLField(blank=True, null=True)
    dl_url = models.URLField('Download URL', help_text='Alternate download url', blank=True, null=True)
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)
    force_i18n = models.BooleanField('Force I18n', default=False, help_text="""
        By default, only Resources that have been associated with a Lesson that
        is itself being internationalized will be internationalized. However, we
        occasionally want to be able to include Resources inline in markdown,
        and those Resources will not be automatically synced.

        Use this flag if for that or any other reason you would like to force a
        Resource to be synced.
    """)

    class Meta:
        ordering = ['name', ]

    @property
    def i18n_key(self):
        return self.slug

    @classmethod
    def internationalizable_fields(cls):
        return ['name', 'url', 'dl_url', 'type']

    @classmethod
    def get_i18n_objects(cls):
        return super(Resource, cls).get_i18n_objects().prefetch_related('lessons', 'lessons__unit')

    @property
    def should_be_translated(self):
        return self.force_i18n or any(lesson.should_be_translated for lesson in self.lessons.all())

    def __unicode__(self):
        '''
        if self.url:
          formatted = "<a href='%s' target='_blank' class='print_link'>%s</a> - %s" % (self.url, self.name, self.type)
        else:
          formatted = "%s - %s" % (self.name, self.type)
        if self.dl_url:
          formatted = "%s (<a href='%s' class='print_link'>%s</a>)" % (formatted, self.dl_url, _("download"))
        elif self.gd:
          formatted = "%s (<a href='%s' class='print_link'>%s</a>)" % (formatted, self.gd_pdf(), _("download"))
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
            formatted = "%s (<a href='%s' class='print_link'>%s</a>)" % (formatted, self.dl_url, _("download"))

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
            formatted = "%s (<a href='%s' class='print_link'>%s</a>)" % (formatted, self.dl_url, _("download"))
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
            doc_id = re.search(RE_DOC, self.url).group('doc_id')
            pdf = 'https://docs.google.com/document/d/%s/export?format=pdf' % doc_id
            return pdf
        except:
            return self.url

    def gd_doc(self):
        try:
            doc_id = re.search(RE_DOC, self.url).group('doc_id')
            pdf = 'https://docs.google.com/document/d/%s/export?format=doc' % doc_id
            return pdf
        except:
            return self.url

    def gd_copy(self):
        try:
            doc_id = re.search(RE_DOC, self.url).group('doc_id')
            pdf = 'https://docs.google.com/document/d/%s/copy' % doc_id
            return pdf
        except:
            return self.url

    def gd_html(self):
        try:
            doc_id = re.search(RE_DOC, self.url).group('doc_id')
            url = 'https://docs.google.com/document/d/%s/export?format=html' % doc_id
            response = urllib2.urlopen(url)
            html = response.read()
            return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, styles=allowed_styles, strip=True)
        except Exception as e:
            print(e)
            return ""

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


class Lesson(InternationalizablePage, RichText, CloneableMixin):
    overview = RichTextField('Lesson Overview')
    short_title = models.CharField('Short Title (optional)', help_text='Used where space is at a premium',
                                   max_length=64, blank=True, null=True)
    duration = models.CharField('Duration', help_text='Duration of lesson',
                                max_length=255, blank=True, null=True)
    week = models.IntegerField('Week', help_text='Week within the unit (only use for first lesson of the week)',
                               blank=True, null=True)
    pacing_weight = models.DecimalField('Pacing Weight', help_text='Higher numbers take up more space pacing calendar',
                                        default=1, max_digits=4, decimal_places=1, blank=True, null=True)
    unplugged = models.BooleanField(default=False)
    resources = SortedManyToManyField(Resource, blank=True, related_name='lessons')
    prep = RichTextField('Preparation', help_text='ToDos for the teacher to prep this lesson', blank=True, null=True)
    assessment = RichTextField('Assessment Opportunities',
                               help_text='Parts of the lesson that can be assessed for students understaning',
                               blank=True, null=True)
    questions = RichTextField('Support Details', help_text='Open questions or comments about this lesson',
                              blank=True, null=True)
    cs_content = RichTextField('Purpose', help_text='Purpose of this lesson in progression and CS in general',
                               blank=True, null=True)
    ancestor = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    standards = models.ManyToManyField(Standard, blank=True)
    anchor_standards = models.ManyToManyField(Standard, help_text='1 - 3 key standards this lesson focuses on',
                                              related_name="anchors", blank=True)
    opportunity_standards = models.ManyToManyField(Standard, help_text='Opportunities for content standards alignment',
                                                   related_name="opportunities", blank=True)
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

    @classmethod
    def get_i18n_objects(cls):
        return super(Lesson, cls).get_i18n_objects().select_related('unit')

    @property
    def should_be_translated(self):
        return self.unit and self.unit.should_be_translated

    @classmethod
    def internationalizable_fields(cls):
        return super(Lesson, cls).internationalizable_fields() + ['overview', 'short_title', 'cs_content', 'prep']

    def __unicode__(self):
        return self.title

    def translated_keywords(self):
        lang = translation.get_language()
        if lang and lang != settings.LANGUAGE_CODE:
            locale = translation.to_locale(lang)
            return [I18nFileWrapper.get_translated_field('Keyword', slugify(keyword), 'title', locale) for keyword in self.keywords.all()]

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

    def parse_xml_block_text(self, str):
        def replace(matchobj):
            # Use single- or double-quotes as the delimiter for our block-text attribute.
            # Note: This means the value of block-text cannot have single- or double-quotes
            # in it.
            match = re.search(r"block-text=[\"\'](?P<block_text>[^\"\']+)[\"\']", matchobj.group(0))
            if match and match.group('block_text'):
                block_text = match.group('block_text')
                return block_text
            else:
                return matchobj.group(0)

        return re.sub(r"(<xml>.+?</xml>)", replace, str, 0, re.DOTALL)

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

                # Use value of block-text attribute in long_instructions to build parsed_long_instructions,
                # which replaces <xml></xml> with block-text, if present.
                long_instructions = level.get('long_instructions')
                if long_instructions:
                    level['parsed_long_instructions'] = self.parse_xml_block_text(long_instructions)

                levels[counter]['levels'].append(level)

            return levels
        else:
            return

    def get_levels_from_levelbuilder(self):
        if not hasattr(self.unit, 'stage_name'):
            return {'error': 'No stage name for unit', 'status': 404}
        else:
            try:
                url = "https://levelbuilder-studio.code.org/s/%s/stage/%d/summary_for_lesson_plans" % (
                    self.unit.stage_name, self.number)
                response = urllib2.urlopen(url)
                data = json.loads(response.read())
                self.stage = data
                self.save()
                return {'status': 200, 'success': 'true'}
            except Exception, e:
                logger.warning("Couldn't get stage details for %s" % self)
                return {'status': 500, 'error': 'failed', 'exception': e.message}

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

    def publish(self, children=False, silent=False):
        if self.jackfrost_can_build():
            for url in self.jackfrost_urls():
                try:
                    read, written = build_single(url)
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

    def clone(self, attrs={}, commit=True, m2m_clone_reverse=True, exclude=[], children=False):
        # If new title and/or slug weren't passed, update
        attrs['title'] = attrs.get('title', "%s (clone)" % self.title)

        # Add default values
        attrs['ancestor'] = self

        # These must be excluded to avoid errors
        exclusions = ['children', 'lesson_set', 'ancestor', 'keywords']
        exclude = exclude + list(set(exclusions) - set(exclude))

        duplicate = super(Lesson, self).clone(attrs=attrs, commit=commit,
                                              m2m_clone_reverse=m2m_clone_reverse, exclude=exclude)

        if children:
            if self.optional_lessons.count() > 0:
                for lesson in self.optional_lessons.all():
                    lesson.clone(attrs={'title': lesson.title, 'parent': duplicate.page_ptr, 'no_renumber': True},
                                 children=True)

        # Keywords are a complex model and don't survive cloning, so we re-add here before returning the clone
        if self.keywords.count() > 0:
            keyword_ids = self.keywords.values_list('keyword__id', flat=True)
            for keyword_id in keyword_ids:
                duplicate.keywords.create(keyword_id=keyword_id)
            duplicate.keywords_string = self.keywords_string
        duplicate.save()

        if not attrs.get('no_renumber', False):
            duplicate.unit.renumber_lessons()

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
        if self.unit.forum_url:
            if self.unit.forum_vars:
                replacements = eval(self.unit.forum_vars)
                return self.unit.forum_url % replacements
            else:
                return self.unit.forum_url
        else:
            return "//forum.code.org/"

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


class Activity(Orderable, CloneableMixin, Internationalizable):
    name = models.CharField(max_length=255)
    content = RichTextField('Activity Content')
    keywords = KeywordsField()
    time = models.CharField(max_length=255, blank=True, null=True)
    lesson = models.ForeignKey(Lesson)
    ancestor = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "activities"
        order_with_respect_to = "lesson"
        unique_together = ('lesson', 'name')

    @classmethod
    def internationalizable_fields(cls):
        return ['name', 'content', 'time']

    @classmethod
    def should_redact(cls):
        return True

    @classmethod
    def get_i18n_objects(cls):
        return super(Activity, cls).get_i18n_objects().select_related('lesson', 'lesson__unit')

    @property
    def should_be_translated(self):
        return self.lesson.should_be_translated

    @property
    def i18n_key(self):
        return "%s/%s" % (self.lesson.i18n_key, self.get_untranslated_field('name'))

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


class Objective(Orderable, Internationalizable, CloneableMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    lesson = models.ForeignKey(Lesson)

    class Meta:
        order_with_respect_to = "lesson"

    @classmethod
    def get_i18n_objects(cls):
        return super(Objective, cls).get_i18n_objects().select_related('lesson', 'lesson__unit')

    @property
    def should_be_translated(self):
        return self.lesson and self.lesson.should_be_translated

    @classmethod
    def internationalizable_fields(cls):
        return ['name']

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
def renumber_post_delete(sender, instance, **kwargs):
    if hasattr(instance, "unit"):
        instance.unit.renumber_lessons()


@receiver(post_save, sender=Lesson)
def renumber_post_create(sender, instance, created, *args, **kwargs):
    if instance.number is None:
        instance.number = instance.get_number()
        instance.save()
        instance.unit.renumber_lessons()


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

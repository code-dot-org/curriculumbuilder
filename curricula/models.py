import re
import logging
import json
import math

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from mezzanine.pages.models import Page, RichText, Orderable, PageMoveException
from mezzanine.core.fields import RichTextField

from jackfrost.receivers import build_page_for_obj
from jackfrost.tasks import build_single

from django_slack import slack_message

from django_cloneable import CloneableMixin

from mezzanine.core.models import Ownable

from standards.models import Standard, GradeBand, Category, Framework
from documentation.models import Map
import lessons.models

from i18n.models import InternationalizablePage

logger = logging.getLogger(__name__)

"""
Curriculum

"""


# TODO(dave): make this implement lessons.models.Filterable
class Curriculum(InternationalizablePage, RichText, CloneableMixin, Ownable):
    CURRENT = 0
    NEXT = 1
    PAST = 2
    VERSION_CHOICES = (
        (CURRENT, 'Current'),
        (NEXT, 'Next'),
        (PAST, 'Past')
    )
    ancestor = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    gradeband = models.ForeignKey(GradeBand, blank=True, null=True, on_delete=models.SET_NULL)
    frameworks = models.ManyToManyField(Framework, blank=True, help_text='Standards frameworks aligned to')
    assessment_commentary = RichTextField('Assessment Commentary', help_text="How this course approaches assessment",
                              blank=True, null=True)
    version = models.IntegerField(choices=VERSION_CHOICES, default=NEXT)
    unit_numbering = models.BooleanField(default=True)
    auto_forum = models.BooleanField(default=False, help_text='Automatically generate forum links?')
    support_script = models.BooleanField(default=False, help_text='Link to support script in Code Studio?')
    display_questions = models.BooleanField(default=False, help_text='Display open questions and feedback form?')
    feedback_url = models.URLField(blank=True, null=True, help_text='URL to feedback form, using % operators')
    feedback_vars = models.CharField(max_length=255, blank=True, null=True,
                                     help_text='Tuple of properties to use in feedback url')
    unit_template_override = models.CharField(max_length=255, blank=True, null=True,
                                              help_text='Override default unit template, eg "curricula/pl_unit.html')
    canonical_slug = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "curricula"
        permissions = [('access_all_curricula', 'Can access all curricula')]

    @classmethod
    def internationalizable_fields(cls):
        return super(Curriculum, cls).internationalizable_fields() + ['assessment_commentary']

    def __unicode__(self):
        return self.title

    def can_access(self, request):
        return request.user.has_perm('curricula.access_all_curricula') or request.user.id == self.user_id

    def can_add(self, request):
        return self.can_access(request)

    def can_change(self, request):
        return self.can_access(request)

    def can_delete(self, request):
        return self.can_access(request)

    def can_move(self, request, new_parent):
        if new_parent is not None:
            msg = 'Curriculum must be a top level object'
            raise PageMoveException(msg)
        # For Curriculum objects in particular, do not let users without
        # access_all_curricula permissions move a Curriculum, even if
        # they own it.
        if not request.user.has_perm('curricula.access_all_curricula'):
            raise PageMoveException('You do not have permission to move curriculum')

    def is_editable(self, request):
        return self.can_access(request) and request.user.has_perm('curricula.change_curriculum')

    def get_absolute_url(self):
        return reverse('curriculum:curriculum_view', args=[self.slug])

    def get_pdf_url(self):
        return reverse('curriculum:curriculum_pdf', args=[self.slug])

    def get_json_url(self):
        return reverse('curriculum:curriculum_element', args=[self.slug])

    def get_standards_url(self):
        return reverse('curriculum:by_curriculum', args=[self.slug])

    def get_standards_csv_url(self):
        return reverse('curriculum:by_curriculum_csv', args=[self.slug])

    def get_resources_url(self):
        return reverse('curriculum:curriculum_resources', args=[self.slug])

    def get_blocks_url(self):
        return reverse('curriculum:curriculum_code', args=[self.slug])

    def get_vocab_url(self):
        return reverse('curriculum:curriculum_vocab', args=[self.slug])

    def get_canonical_slug(self):
        return self.canonical_slug or self.slug

    def renumber_units(self):
        for unit in Unit.objects.filter(parent=self.page_ptr)\
                .order_by('parent___order', '_order'):

            # Check for lessons that have been moved here
            if unit.curriculum.pk != self.pk:
                unit.curriculum = self
                unit.save()

        # Renumber units that are actually under the curriculum
        for i, unit in enumerate(self.unit_set.all().order_by('parent___order', '_order')):
            Unit.objects.filter(id=unit.id).update(number=i+1)

    def get_levels_from_levelbuilder(self):
        payload = {
            'status': 200,
            'stages': []
        }

        for lesson in self.lesson_set.all():
            stage_payload = lesson.get_levels_from_levelbuilder()
            payload['stages'].append(stage_payload)
            if stage_payload['status'] != 200: payload['status'] = stage_payload['status']

        return payload

    # Return publishable urls for JackFrost
    def jackfrost_urls(self):
        urls = [self.get_absolute_url(), self.get_standards_url(), self.get_standards_csv_url(),
                self.get_resources_url(), self.get_blocks_url(), self.get_vocab_url(), self.get_json_url()]
        return urls

    def jackfrost_can_build(self):
        return settings.ENABLE_PUBLISH and self.status == 2 and not self.login_required

    def publish(self, children=False, silent=False):
        if children:
            for unit in self.units:
                for result in unit.publish(children=True):
                    yield result
        if self.jackfrost_can_build():
            try:
                read, written = build_page_for_obj(Curriculum, self)
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

    def get_standards(self):
        # ToDo: run the standards queries once and place all the querysets in a dict for later use
        if Chapter.objects.filter(parent__unit__curriculum=self).count() > 0:
            grouper = "Chapter"
        else:
            grouper = "Course"

        columns = [{"title": grouper, "field": "chapter", "frozen": True, "tooltips": False, "headerSort": False, "width": 100}]
        for fw in self.frameworks.all():
            group = {
                    "title": fw.slug,
                    "columns": [{"title": cat.shortcode,
                                 "field": "%s-%s" % (fw.slug, cat.shortcode),
                                 "headerSort": False,
                                 "formatter": "heatCell",
                                 "align": "center",
                                 "tooltipHeader": cat.name,
                                 "total": cat.standards.count()}
                                for cat in fw.categories.bottom()]
            }
            columns.append(group)

        rows = []
        keys = ["chapter"] + ["%s-%s" % (fw.slug, cat.shortcode) for fw in self.frameworks.all() for cat in
                              fw.categories.bottom()]
        for unit in self.units:
            if unit.chapters:
                for chapter in unit.chapters:
                    values = ["U%sCh%s" % (unit.number, chapter.number)] +\
                             [json.dumps(list(cat.standards.filter(lesson__in=chapter.lessons)
                                              .distinct().values_list("shortcode", flat=True)))
                              for fw in self.frameworks.all() for cat in fw.categories.bottom()]
                    row = dict(zip(keys, values))
                    rows.append(row)
            else:
                values = [unit.title] + \
                         [json.dumps(list(cat.standards.filter(Q(lesson__in=unit.lessons) |
                                                               Q(opportunities__in=unit.lessons))
                                          .distinct().values_list("shortcode", flat=True)))
                          for fw in self.frameworks.all() for cat in fw.categories.bottom()]
                row = dict(zip(keys, values))
                rows.append(row)

        return columns, rows

    @property
    def maps(self):
        return Map.objects.filter(parent=self)

    @property
    def units(self):
        return Unit.objects.filter(parent=self, login_required=False)

    @property
    def should_be_translated(self):
        return any(unit.should_be_translated for unit in self.units)

    # Hijacking the Mezzanine top menu to control which curricula show on the home page
    @property
    def in_main_menu(self):
        return '1' in self.in_menus

    def clone(self, attrs={}, commit=True, m2m_clone_reverse=True, exclude=[], children=False):

        # If new title, slug, or version weren't passed, update
        attrs['title'] = attrs.get('title', "%s (clone)" % self.title)
        attrs['slug'] = attrs.get('slug', "%s_clone" % self.slug)
        attrs['version'] = attrs.get('version', Curriculum.NEXT)

        # Add default values
        attrs['ancestor'] = self

        # These must be excluded to avoid errors
        exclusions = ['children', 'units', 'ancestor']
        exclude = exclude + list(set(exclusions) - set(exclude))

        duplicate = super(Curriculum, self).clone(attrs=attrs, commit=commit,
                                                  m2m_clone_reverse=m2m_clone_reverse, exclude=exclude)

        if children:
            for unit in self.units.all():
                unit.clone(attrs={'title': unit.title, 'slug': unit.slug,'parent': duplicate.page_ptr,
                                  'no_renumber': True}, children=True)

            for map in self.maps.all():
                map.clone(attrs={'slug': map.slug, 'title': map.title, 'parent': duplicate.page_ptr}, children=True)

        # Keywords are a complex model and don't survive cloning, so we re-add here before returning the clone
        if self.keywords.count() > 0:
            keyword_ids = self.keywords.values_list('keyword__id', flat=True)
            for keyword_id in keyword_ids:
                duplicate.keywords.create(keyword_id=keyword_id)
            duplicate.keywords_string = self.keywords_string
        duplicate.save()

        return duplicate


"""
Curricular Unit

"""


# TODO(dave): make this implement lessons.models.Filterable
class Unit(InternationalizablePage, RichText, CloneableMixin, Ownable):
    curriculum = models.ForeignKey(Curriculum, blank=True, null=True)
    ancestor = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    disable_numbering = models.BooleanField(default=False, help_text="Override to disable unit numbering")
    number = models.IntegerField('Number', blank=True, null=True)
    stage_name = models.CharField('Script', max_length=255, blank=True, null=True,
                                  help_text='Name of Code Studio script')
    questions = RichTextField('Support Details', help_text='Open questions or comments to add to all lessons in unit',
                              blank=True, null=True)
    assessment_commentary = RichTextField('Assessment Commentary', help_text="How this unit approaches assessment",
                              blank=True, null=True)
    show_calendar = models.BooleanField('Show Calendar', default=False, help_text='Show pacing guide calendar?')
    week_length = models.IntegerField('Days in a Week', default=5, blank=True, null=True,
                                      help_text='Controls the minimum lesson size in the pacing calendar.')
    forum_url = models.URLField(blank=True, null=True, help_text='URL to forum, using % operators')
    forum_vars = models.CharField(max_length=255, blank=True, null=True,
                                  help_text='Tuple of properties to use in forum url')
    lesson_template_override = models.CharField(max_length=255, blank=True, null=True,
                                                help_text='Override default lesson template,'
                                                          'eg curricula/pl_lesson.html')
    i18n_ready = models.BooleanField(default=False, help_text="Ready for internationalization")

    class Meta:
        permissions = [('access_all_units', 'Can access all units')]

    @classmethod
    def internationalizable_fields(cls):
        return super(Unit, cls).internationalizable_fields() + ['assessment_commentary']

    def __unicode__(self):
        return self.title

    @property
    def should_be_translated(self):
        return self.i18n_ready

    @property
    def has_resource_pdf(self):
        return self.curriculum.slug not in ['csf-18', 'csf-1718', 'hoc']

    def can_access(self, request):
        return request.user.has_perm('curricula.access_all_units') or request.user.id == self.user_id

    def can_add(self, request):
        return self.can_access(request)

    def can_change(self, request):
        return self.can_access(request)

    def can_delete(self, request):
        return self.can_access(request)

    def can_move(self, request, new_parent):
        parent_type = getattr(new_parent, 'content_model', None)
        if not parent_type == 'curriculum':
            msg = 'Unit must live directly under a curriculum'
            raise PageMoveException(msg)
        if not self.can_access(request):
            raise PageMoveException('Cannot move a unit you do not own')
        if not Page.get_content_model(new_parent).can_access(request):
            raise PageMoveException('Cannot move a unit to a curriculum you do not own')

    def is_editable(self, request):
        return self.can_access(request) and request.user.has_perm('curricula.change_unit')

    def get_absolute_url(self):
        return reverse('curriculum:unit_view', args=[self.curriculum.slug, self.slug])

    def get_compiled_url(self):
        return reverse('curriculum:unit_compiled', args=[self.curriculum.slug, self.slug])

    def get_pdf_url(self):
        return reverse('curriculum:unit_pdf', args=[self.curriculum.slug, self.slug])

    def get_json_url(self):
        return reverse('curriculum:stage_element', args=[self.stage_name])

    def get_resources_pdf_url(self):
        return reverse('curriculum:unit_resources_pdf', args=[self.curriculum.slug, self.slug])

    def get_resources_url(self):
        return reverse('curriculum:unit_resources', args=[self.curriculum.slug, self.slug])

    def get_blocks_url(self):
        return reverse('curriculum:unit_code', args=[self.curriculum.slug, self.slug])

    def get_vocab_url(self):
        return reverse('curriculum:unit_vocab', args=[self.curriculum.slug, self.slug])

    def get_standards_url(self):
        return reverse('curriculum:by_unit_2', args=[self.curriculum.slug, self.slug])

    def get_standards_csv_url(self):
        return reverse('curriculum:by_unit_csv', args=[self.curriculum.slug, self.slug])

    def get_number(self):
        order = 1
        for unit in self.curriculum.units.all().order_by('parent___order', '_order'):
            if unit == self:
                break
            else:
                order += 1
        return order

    def get_unit_numbering(self):
        if self.curriculum.unit_numbering and not self.disable_numbering:
            return "Unit %d" % self.number
        else:
            return

    def renumber_lessons(self):
        if self.chapters.count() > 0:
            for i, chapter in enumerate(self.chapters.all()):
                Chapter.objects.filter(id=chapter.id).update(number=i+1)
                for lesson in lessons.models.Lesson.objects.filter(parent=chapter.page_ptr)\
                                                                   .order_by('parent___order', '_order'):

                    # Check for lessons that have been moved here
                    if lesson.unit.pk != self.pk:
                        lesson.unit = self
                        lesson.save()
        else:
            for lesson in lessons.models.Lesson.objects.filter(parent=self.page_ptr)\
                                                               .order_by('parent___order', '_order'):

                # Check for lessons that have been moved here
                if lesson.unit.pk != self.pk:
                    lesson.unit = self
                    lesson.save()

        # Renumber lessons that are actually under the unit
        for i, lesson in enumerate(self.lesson_set.all().order_by('parent___order', '_order')):
            lessons.models.Lesson.objects.filter(id=lesson.id).update(number=i+1)

    def get_levels_from_levelbuilder(self):
        payload = {
            'status': 200,
            'stages': []
        }

        for lesson in self.lesson_set.all():
            stage_payload = lesson.get_levels_from_levelbuilder()
            payload['stages'].append(stage_payload)
            if stage_payload['status'] != 200: payload['status'] = stage_payload['status']

        return payload

    # Return publishable urls for JackFrost
    def jackfrost_urls(self):
        urls = [self.get_absolute_url(), self.get_resources_url(), self.get_blocks_url(),
                self.get_vocab_url(), self.get_standards_url(), self.get_standards_csv_url(),
                self.get_compiled_url(), self.get_json_url()]
        return urls

    def pdf_urls(self):
        return [self.get_pdf_url(), self.get_resources_pdf_url()]

    def jackfrost_can_build(self):
        return settings.ENABLE_PUBLISH and self.status == 2 and not self.login_required and not self.curriculum.login_required

    def publish(self, children=False, silent=False):
        if children:
            for lesson in self.lesson_set.all():
                for result in lesson.publish():
                    yield result
        if self.jackfrost_can_build():
            for url in self.jackfrost_urls():
                try:
                    read, written = build_single(url)
                    if not silent:
                        slack_message('slack/message.slack', {
                            'message': 'published %s %s %s' % (self.content_model, self.title, url),
                            'color': '#00adbc'
                        })
                    yield json.dumps(written)
                    yield '\n'
                except Exception, e:
                    yield json.dumps(e.message)
                    yield '\n'
                    logger.exception('Failed to publish %s' % self)

    def publish_pdfs(self, silent=False, *args, **kwargs):
        if self.jackfrost_can_build():
            for url in self.pdf_urls():
                try:
                    read, written = build_single(url)
                    if not silent:
                        slack_message('slack/message.slack', {
                            'message': 'published PDF for %s %s' % (self.content_model, self.title),
                            'color': '#00adbc'
                        })
                    yield json.dumps(written)
                    yield '\n'
                except Exception, e:
                    yield json.dumps(e.message)
                    yield '\n'
                    logger.exception('Failed to publish PDF %s' % self)

    def publish_json(self, silent=False, *args, **kwargs):
        if self.jackfrost_can_build():
            url = self.get_json_url()
            try:
                read, written = build_single(url)
                if not silent:
                    slack_message('slack/message.slack', {
                        'message': 'published JSON for %s %s' % (self.content_model, self.title),
                        'color': '#00adbc'
                    })
                yield json.dumps(written)
                yield '\n'
            except Exception, e:
                yield json.dumps(e.message)
                yield '\n'
                logger.exception('Failed to publish JSON %s' % self)

    def get_standards(self):
        # ToDo: run the standards queries once and place all the querysets in a dict for later use

        frameworks = self.curriculum.frameworks.all().prefetch_related('categories', 'categories__standards')

        columns = [{"title": "Lesson", "field": "lesson", "frozen": True, "tooltips": False, "headerSort": False, "width": 100}]
        for fw in frameworks:
            group = {
                    "title": fw.slug,
                    "columns": [{"title": cat.shortcode,
                                 "field": "%s-%s" % (fw.slug, cat.shortcode),
                                 "headerSort": False,
                                 "formatter": "heatCell",
                                 "align": "center",
                                 "tooltipHeader": cat.name,
                                 "total": cat.standards.count()}
                                for cat in fw.categories.bottom()]
            }
            columns.append(group)

        rows = []
        keys = ["lesson"] + ["%s-%s" % (fw.slug, cat.shortcode) for fw in frameworks for cat in fw.categories.bottom()]
        for lesson in self.lessons:
            values = ["Lesson %d" % lesson.number] + \
                     [json.dumps(list(cat.standards.filter(Q(lesson__in=[lesson]) |
                                                           Q(opportunities__in=[lesson]))
                                      .distinct().values_list("shortcode", flat=True)))
                      for fw in frameworks for cat in fw.categories.bottom()]
            row = dict(zip(keys, values))
            rows.append(row)

        return columns, rows

    @property
    def short_name(self):
        if self.curriculum.unit_numbering and not self.disable_numbering:
            return self.get_unit_numbering()
        else:
            return self.title

    @property
    def long_name(self):
        if self.curriculum.unit_numbering and not self.disable_numbering:
            return "%s - %s" % (self.get_unit_numbering(), self.title)
        else:
            return self.title

    @property
    def support_script(self):
        return "https://studio.code.org/s/%s-support" % getattr(self, 'stage_name', self.slug)

    @property
    def header_corner(self):
        header = ''
        if self.curriculum.unit_numbering and not self.disable_numbering:
            header = "<span class='h2'>Unit</span><span class='h1'>%d</span>" % self.number
        else:
            title_words = self.title.split()
            for i, word in enumerate(title_words):
                if i < 1 or i > 1:
                    header += "<span class='h2'>%s</span>" % word
                else:
                    header += "<span class='h1'>%s</span>" % word
        return header

    @property
    def block_count(self):
        num_blocks = self.lessons.aggregate(Count('blocks'))
        return num_blocks.get('blocks__count')

    @property
    def vocab_count(self):
        num_blocks = self.lessons.aggregate(Count('vocab'))
        return num_blocks.get('vocab__count')

    @property
    def lesson_width(self):
        return (100 / self.week_length) - 1

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

    def clone(self, attrs={}, commit=True, m2m_clone_reverse=True, exclude=[], children=False):

        # If new title and/or slug weren't passed, update
        attrs['title'] = attrs.get('title', "%s (clone)" % self.title)
        attrs['slug'] = attrs.get('slug', "%s_clone" % self.slug)

        # Add default values
        attrs['ancestor'] = self

        # These must be excluded to avoid errors
        exclusions = ['children', 'lessons', 'chapters']
        exclude = exclude + list(set(exclusions) - set(exclude))

        if not attrs.get('slug', False):
            # Check for slug uniqueness, if not unique append number
            for x in range(1, 100):
                if self.curriculum.units.filter(slug=attrs['slug']).count() == 0:
                    break
                attrs['slug'] = '%s-%d' % (attrs['slug'][:250], x)

        duplicate = super(Unit, self).clone(attrs=attrs, commit=commit,
                                            m2m_clone_reverse=m2m_clone_reverse, exclude=exclude)
        if children:
            if self.chapters.count() > 0:
                for chapter in self.chapters.all():
                    chapter.clone(attrs={'title': chapter.title, 'parent': duplicate.page_ptr, 'no_renumber': True},
                                  children=True)
            else:
                for lesson in self.lessons.all():
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
            duplicate.curriculum.renumber_units()

        return duplicate


"""
Unit Chapter

"""


# TODO(dave): make this implement lessons.models.Filterable
class Chapter(InternationalizablePage, RichText, CloneableMixin, Ownable):
    ancestor = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    number = models.IntegerField('Number', blank=True, null=True)
    questions = RichTextField(blank=True, null=True, help_text="md list of big questions")
    understandings = models.ManyToManyField(Category, blank=True)
    _old_slug = models.CharField('old_slug', max_length=2000, blank=True, null=True)

    class Meta:
        order_with_respect_to = "parent"
        permissions = [('access_all_chapters','Can access all chapters')]

    @classmethod
    def internationalizable_fields(cls):
        return super(Chapter, cls).internationalizable_fields() + ['questions']

    def __unicode__(self):
        return self.title

    def can_access(self, request):
        return request.user.has_perm('curricula.access_all_chapters') or request.user.id == self.user_id

    def can_add(self, request):
        return self.can_access(request)

    def can_change(self, request):
        return self.can_access(request)

    def can_delete(self, request):
        return self.can_access(request)

    def can_move(self, request, new_parent):
        parent_type = getattr(new_parent, 'content_model', None)
        if not parent_type == 'unit':
            msg = 'Chapter must live directly under a unit'
            raise PageMoveException(msg)
        if not self.can_access(request):
            raise PageMoveException('Cannot move a chapter you do not own')
        if not Page.get_content_model(new_parent).can_access(request):
            raise PageMoveException('Cannot move a chapter to a unit you do not own')

    def is_editable(self, request):
        return self.can_access(request) and request.user.has_perm('curricula.change_chapter')

    def get_absolute_url(self):
        return reverse('curriculum:chapter_view', args=[self.unit.curriculum.slug, self.unit.slug, self.number])

    def get_number(self):
        order = 1
        for chapter in self.unit.chapters.all().order_by('parent___order', '_order'):
            if chapter == self:
                break
            else:
                order += 1
        return order

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

    def clone(self, attrs={}, commit=True, m2m_clone_reverse=True, exclude=[], children=False):

        # If new title and/or slug weren't passed, update
        attrs['title'] = attrs.get('title', "%s (clone)" % self.title)

        # Add default values
        attrs['ancestor'] = self

        # These must be excluded to avoid errors
        exclusions = ['children', 'lessons', 'ancestors']
        exclude = exclude + list(set(exclusions) - set(exclude))

        duplicate = super(Chapter, self).clone(attrs=attrs, commit=commit,
                                               m2m_clone_reverse=m2m_clone_reverse, exclude=exclude)

        if children:
            for lesson in self.lessons.all():
                lesson.clone(attrs={'title': lesson.title, 'parent': duplicate.page_ptr,'no_renumber': True},
                             children=True)

        if not attrs.get('no_renumber', False):
            print("renumbering lessons")
            duplicate.unit.renumber_lessons()

        # Keywords are a complex model and don't survive cloning, so we re-add here before returning the clone
        if self.keywords.count() > 0:
            keyword_ids = self.keywords.values_list('keyword__id', flat=True)
            for keyword_id in keyword_ids:
                duplicate.keywords.create(keyword_id=keyword_id)
            duplicate.keywords_string = self.keywords_string
        duplicate.save()

        return duplicate


"""
Topics that provide additional curriculum, unit, or chapter info

"""


class Topic(Orderable, CloneableMixin):
    name = models.CharField(max_length=255)
    content = RichTextField('Topic Content')
    page = models.ForeignKey(Page, related_name='topics')

    class Meta:
        verbose_name_plural = "topics"
        order_with_respect_to = "page"

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            old_topic = Topic.objects.get(pk=self.pk)
            if old_topic._order != self._order:
                logger.debug('Activity order changing! Activity %s, lesson %s' % (self.pk, self.lesson.pk))
        except:
            pass
        super(Topic, self).save(*args, **kwargs)


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

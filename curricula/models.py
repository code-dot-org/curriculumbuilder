from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from mezzanine.pages.models import Page, RichText, Orderable, PageMoveException
from mezzanine.core.fields import RichTextField
from jackfrost.utils import build_page_for_obj
from jackfrost.tasks import build_single
from standards.models import Standard, GradeBand, Category, Framework
import lessons.models

"""
Curriculum

"""


class Curriculum(Page, RichText):
    gradeband = models.ForeignKey(GradeBand)
    frameworks = models.ManyToManyField(Framework, blank=True, help_text='Standards frameworks aligned to')
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

    def get_standards_url(self):
        return '/%s/standards/' % self.slug

    # Return publishable urls for JackFrost
    def jackfrost_urls(self):
        urls = [self.get_absolute_url(), self.get_standards_url()]
        return urls

    def jackfrost_can_build(self):
        return self.status == 2 and not self.login_required

    def publish(self, children=False):
        response = {}
        if children:
            for unit in self.units:
                response[unit.title] = unit.publish(True)
        if self.jackfrost_can_build():
            read, written = build_page_for_obj(Curriculum, self)
            for result in written:
                response[result.name] = result
        return response

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

    def get_pdf_url(self):
        return '%s%s.pdf' % (self.curriculum.get_absolute_url(), self.slug)

    def get_resources_url(self):
        return '%s%s_resources.pdf' % (self.curriculum.get_absolute_url(), self.slug)

    def get_number(self):
        return int(self._order) + 1

    # Return publishable urls for JackFrost
    def jackfrost_urls(self):
        urls = [self.get_absolute_url(), self.get_pdf_url(), self.get_resources_url()]
        return urls

    def jackfrost_can_build(self):
        return self.status == 2 and not self.login_required and not self.curriculum.login_required

    def publish(self, children=False):
        response = {}
        if children:
            for lesson in self.lesson_set.all():
                response[lesson.title] = lesson.publish()
        if self.jackfrost_can_build():
            read, written = build_page_for_obj(Unit, self)
            for result in written:
                response[result.name] = result
        return response

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
        return self.status == 2 and not self.login_required

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

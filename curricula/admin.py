from django.contrib import admin
from django.forms import ModelForm
from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from mezzanine.generic.fields import KeywordsField
from import_export.admin import ImportExportModelAdmin

from reversion.admin import VersionAdmin

from lessons.models import Lesson
from lessons.admin import LessonForm

from curricula.models import Curriculum, Unit, Chapter, FrontMatter, Topic
from standards.models import Standard


class LessonInline(TabularDynamicInlineAdmin):
    model = Lesson
    fk_name = 'unit'
    fields = ['number', 'title', 'week', 'pacing_weight', 'unplugged', 'keywords']

    keywords = KeywordsField()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LessonStandardsInline(StackedDynamicInlineAdmin):
    model = Lesson
    form = LessonForm
    fk_name = 'unit'
    fields = ('standards',)
    filter_horizontal = ('standards',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class TopicInline(TabularDynamicInlineAdmin):
    model = Topic
    verbose_name_plural = "Topics"
    extra = 5


class CurriculumAdmin(PageAdmin, VersionAdmin):
    model = Curriculum
    verbose_name_plural = "Curricula"
    filter_horizontal = ('frameworks',)
    inlines = (TopicInline,)


class UnitAdmin(PageAdmin, VersionAdmin):
    model = Unit
    inlines = (TopicInline, )


class ChapterAdmin(PageAdmin):
    model = Chapter
    filter_horizontal = ('understandings',)
    inlines = (TopicInline,)

    fieldsets = (
        (None, {
            'fields': ['title', 'status', 'content', 'questions', 'understandings'],
        }),
    )


class FrontMatterAdmin(PageAdmin, VersionAdmin):
    model = FrontMatter
    inlines = (TopicInline, )


'''
UnitStandards allows for quick standards aligning without the ability to edit actual lesson content
'''


class UnitStandardsForm(ModelForm):
    class Meta:
        model = Unit
        fields = ('title',)


class UnitStandards(Unit):
    class Meta:
        proxy = True
        verbose_name = u'Unit Standards'
        verbose_name_plural = u'Unit Standards'


class UnitStandardsAdmin(ImportExportModelAdmin):
    list_display = ('title', 'curriculum', 'number')
    list_filter = ('curriculum', 'curriculum__version')
    list_editable = ()
    readonly_fields = ('title',)
    inlines = (LessonStandardsInline,)
    form = UnitStandardsForm

    def get_changelist_form(self, request, **kwargs):
        return UnitStandardsForm

admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(FrontMatter, FrontMatterAdmin)
admin.site.register(UnitStandards, UnitStandardsAdmin)
# admin.site.register(UnitLesson)

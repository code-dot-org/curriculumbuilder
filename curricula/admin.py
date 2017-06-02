from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from mezzanine.generic.fields import KeywordsField

from reversion.admin import VersionAdmin

from lessons.models import Lesson

from curricula.models import Curriculum, Unit, Chapter


class LessonInline(TabularDynamicInlineAdmin):
    model = Lesson
    fk_name = 'unit'
    fields = ['number', 'title', 'week', 'pacing_weight', 'unplugged', 'keywords']

    keywords = KeywordsField()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CurriculumAdmin(PageAdmin, VersionAdmin):
    model = Curriculum
    verbose_name_plural = "Curricula"
    filter_horizontal = ('frameworks',)


class UnitAdmin(PageAdmin, VersionAdmin):
    model = Unit
    inlines = [LessonInline, ]


class ChapterAdmin(PageAdmin):
    model = Chapter
    filter_horizontal = ('understandings',)

    fieldsets = (
        (None, {
            'fields': ['title', 'status', 'content', 'questions', 'understandings'],
        }),
    )


admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Chapter, ChapterAdmin)
# admin.site.register(UnitLesson)

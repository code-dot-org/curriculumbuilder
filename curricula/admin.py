from django.contrib import admin
from mezzanine.pages.admin import PageAdmin

from reversion.admin import VersionAdmin

from curricula.models import Curriculum, Unit, Chapter


class CurriculumAdmin(PageAdmin, VersionAdmin):
    model = Curriculum
    verbose_name_plural = "Curricula"
    filter_horizontal = ('frameworks',)


class UnitAdmin(PageAdmin, VersionAdmin):
    model = Unit


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

from django.contrib import admin
from mezzanine.pages.admin import PageAdmin

from curricula.models import Curriculum, Unit, Chapter


class CurriculumAdmin(PageAdmin):
    model = Curriculum
    verbose_name_plural = "Curricula"
    filter_horizontal = ('frameworks',)


class UnitAdmin(PageAdmin):
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

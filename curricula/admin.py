from django.contrib import admin

from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from curricula.models import Curriculum, Unit, UnitLesson

class LessonInline(TabularDynamicInlineAdmin):
  model = UnitLesson

class UnitInline(TabularDynamicInlineAdmin):
  model = Unit
  fk_name = 'curriculum'

  fieldsets = (
    (None, {
      'fields': ['title',]
    }),
  )

class CurriculumAdmin(PageAdmin):
  model = Curriculum
  inlines = [UnitInline]
  verbose_name_plural = "Curricula"

class UnitAdmin(PageAdmin):
  model = Unit
  inlines = [LessonInline]
  list_display = ('title', 'curriculum', 'status')
  list_filter = ('title', 'curriculum',)

admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(Unit, UnitAdmin)
#admin.site.register(UnitLesson)
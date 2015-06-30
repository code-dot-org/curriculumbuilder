from django.contrib import admin
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

class CurriculumAdmin(admin.ModelAdmin):
  model = Curriculum
  inlines = [UnitInline]
  verbose_name_plural = "Curricula"

class UnitAdmin(admin.ModelAdmin):
  model = Unit
  inlines = [LessonInline]
  list_display = ('curriculum',)
  list_filter = ('curriculum',)

admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(Unit, UnitAdmin)
#admin.site.register(UnitLesson)
from django.contrib import admin

from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from curricula.models import Curriculum, Unit, Chapter

class CurriculumAdmin(PageAdmin):
  model = Curriculum
  verbose_name_plural = "Curricula"

class UnitAdmin(PageAdmin):
  model = Unit

class ChapterAdmin(PageAdmin):
  model = Chapter

admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Chapter, ChapterAdmin)
#admin.site.register(UnitLesson)
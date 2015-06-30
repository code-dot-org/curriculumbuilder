from django.contrib import admin

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from standards.models import Framework, Category, Standard, Grade, GradeBand

class StandardInline(TabularDynamicInlineAdmin):
  model = Standard

class CategoryInline(TabularDynamicInlineAdmin):
  model = Category
  verbose_name_plural = "Categories"
  inlines = [StandardInline]

class CategoryAdmin(admin.ModelAdmin):
  model = Category
  list_display = ('name', 'framework', 'parent', 'shortcode')
  list_filter = ('framework', 'parent')
  inlines = [StandardInline]

class FrameworkAdmin(admin.ModelAdmin):
  model = Framework
  inlines = [CategoryInline]

class StandardResource(resources.ModelResource):

  # category = fields.Field(column_name='category', attribute='shortcode',
  #                         widget = ForeignKeyWidget(Category,'shortcode'))

  class Meta:
    model = Standard
    fields = ('id', 'shortcode', 'name', 'description', 'category', 'gradeband',)

class StandardAdmin(ImportExportModelAdmin):
  resource_class = StandardResource
  list_display = ('framework', 'category', 'slug', 'name')
  list_filter = ('framework', 'category', 'gradeband')
  pass

admin.site.register(Standard, StandardAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Framework, FrameworkAdmin)
admin.site.register(GradeBand)
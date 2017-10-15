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

    '''
    def before_import(self, dataset, dry_run, **kwargs):
      i = 0
      last = dataset.height - 1

      while i <= last:

        try:
          gradeband = GradeBand.objects.get(shortcode=dataset.get_col(3)[0])
        except GradeBand.DoesNotExist:
          gradeband = GradeBand.objects.all()[0]

        try:
          category = Category.objects.get(name=dataset.get_col(4)[0])
        except Category.DoesNotExist:
          category = Category.objects.all()[0]

        dataset.rpush((
          dataset.get_col(1)[0],
          dataset.get_col(2)[0],
          gradeband.pk,
          category.pk,
          dataset.get_col(5)[0],
          dataset.get_col(6)[0],
        ))
        i = i + 1
    '''

    category = fields.Field(column_name='category', attribute='category',
                            widget = ForeignKeyWidget(Category, 'name'))
  
    gradeband = fields.Field(column_name='gradeband', attribute='gradeband',
                             widget = ForeignKeyWidget(GradeBand, 'name'))

    class Meta:
        model = Standard
        fields = ('id', 'framework__slug', 'category', 'gradeband', 'shortcode', 'name', 'description')


class StandardAdmin(ImportExportModelAdmin):
    resource_class = StandardResource
    list_display = ('framework', 'category', 'shortcode', 'name', 'description')
    list_filter = ('framework', 'category', 'gradeband')
    list_editable = ('shortcode', 'name', 'description')
    pass


admin.site.register(Standard, StandardAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Framework, FrameworkAdmin)
admin.site.register(GradeBand)

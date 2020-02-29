from __future__ import print_function
from django.contrib import admin

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from standards.models import Framework, Category, Standard, Grade, GradeBand


# Need to override default django-import-export foreignkey widget
# in order to lookup categories by both shortcode and framework
# to account for duplicate shortcodes used across different frameworks

class CategoryForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row, *args, **kwargs):
        print(row)
        return self.model.objects.filter(
            framework__slug__iexact=row["framework"],
            shortcode__iexact=row["category"]
        )


class CategoryParentForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row, *args, **kwargs):
        print(row)
        return self.model.objects.filter(
            framework__slug__iexact=row["framework"],
            shortcode__iexact=row["parent"]
        )


class StandardInline(TabularDynamicInlineAdmin):
    model = Standard


class CategoryInline(TabularDynamicInlineAdmin):
    model = Category


class CategoryResource(resources.ModelResource):

    parent = fields.Field(column_name='parent', attribute='parent',
                          widget=CategoryParentForeignKeyWidget(Category, 'shortcode'))
    framework = fields.Field(column_name='framework', attribute='framework',
                             widget=ForeignKeyWidget(Framework, 'slug'))

    class Meta:
        model = Category
        fields = ('id', 'framework', 'parent', 'type', 'shortcode', 'name', 'description')


class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('name', 'framework', 'parent', 'shortcode')
    list_filter = ('framework', 'parent')
    inlines = [CategoryInline, StandardInline]

    class Meta:
        model = Category
        fields = ('id', 'framework__slug', 'parent', 'type', 'shortcode', 'name', 'description')


class FrameworkAdmin(admin.ModelAdmin):
    model = Framework
    inlines = [CategoryInline]


class StandardResource(resources.ModelResource):
    category = fields.Field(column_name='category', attribute='category',
                            widget=CategoryForeignKeyWidget(Category, 'shortcode'))
    gradeband = fields.Field(column_name='gradeband', attribute='gradeband',
                             widget=ForeignKeyWidget(GradeBand, 'name'))
    framework = fields.Field(column_name='framework', attribute='framework',
                             widget=ForeignKeyWidget(Framework, 'slug'))

    class Meta:
        model = Standard
        fields = ('id', 'framework', 'category', 'gradeband', 'shortcode', 'name', 'description')


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

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


class CategoryResource(resources.ModelResource):
    parent = fields.Field(column_name='parent', attribute='parent',
                          widget=ForeignKeyWidget(Category, 'shortcode'))

    class Meta:
        model = Category
        fields = ('id', 'framework__slug', 'parent', 'type', 'shortcode', 'name', 'description')


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
                            widget=ForeignKeyWidget(Category, 'shortcode'))

    gradeband = fields.Field(column_name='gradeband', attribute='gradeband',
                             widget=ForeignKeyWidget(GradeBand, 'name'))

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

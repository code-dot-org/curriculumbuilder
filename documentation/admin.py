from django.contrib import admin
from django.db import models
from django.forms import Textarea, ModelForm, TextInput
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin

from reversion.admin import VersionAdmin

from lessons.models import Resource

from documentation.models import Block, IDE, Category, Parameter, Example, Map


class CategoryInline(TabularDynamicInlineAdmin):
    model = Category
    verbose_name = "Category"
    verbose_name_plural = "Categories"
    extra = 3


class ParameterInline(StackedDynamicInlineAdmin):
    model = Parameter
    extra = 3


class ExampleInline(StackedDynamicInlineAdmin):
    model = Example
    extra = 3


class IDEAdmin(PageAdmin, VersionAdmin):
    model = IDE

    inlines = [CategoryInline, ]

    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'language', ('description', 'gen_description')],
        }),
        ('Documentation', {
            'fields': ['url', 'content'],
        }),
    )


class BlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)

        if self.instance.parent:
            categories_queryset = Category.objects.filter(parent_ide=self.instance.parent.ide)
        else:
            categories_queryset = Category.objects.all()

        if self.instance.parent_cat:
            parent_obj_queryset = Block.objects.filter(parent_cat=self.instance.parent_cat)
        elif self.instance.parent_ide:
            parent_obj_queryset = Block.objects.filter(parent_ide=self.instance.parent_ide)
        else:
            parent_obj_queryset = Block.objects.all()

        videos_queryset = Resource.objects.filter(type__iexact="video")

        if self.fields.get('parent_cat', False):
            self.fields['parent_cat'].queryset = categories_queryset
        if self.fields.get('parent_object', False):
            self.fields['parent_object'].queryset = parent_obj_queryset
        if self.fields.get('video', False):
            self.fields['video'].queryset = videos_queryset


class BlockAdmin(PageAdmin, VersionAdmin):
    form = BlockForm

    inlines = [ParameterInline, ExampleInline]

    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'video', 'image', ('description', 'gen_description')],
        }),
        ('Documentation', {
            'fields': ['parent_object', 'proxy', 'ext_doc', 'parent_cat', 'content'],
        }),
        ('Details', {
            'fields': ['syntax', 'return_value'],
            'classes': ['collapse-closed'],
        }),
        ('Tips', {
            'fields': ['tips', ],
            'classes': ['collapse-closed'],
        }),
    )

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2})},
    }


class MapAdmin(PageAdmin, VersionAdmin):
    model = Map
    filter_horizontal = ('blocks',)

    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'keywords', 'blocks', 'content', 'in_menus'],
        }),
    )


class BlockDocForm(ModelForm):
    class Meta:
        model = Block
        fields = ["parent_ide", 'title', 'syntax', "parent_cat", 'ext_doc', 'proxy']
        ordering = ('parent_ide', '_order')
        widgets = {
            'syntax': Textarea(attrs={'cols': '10'}),
            'ext_doc': TextInput(attrs={'size': '10'})
        }


class BlockDoc(Block):
    class Meta:
        proxy = True


class BlockDocAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent_ide', 'parent_cat')
    list_filter = ('parent_ide', 'parent_cat')
    ordering = ('parent_ide', '_order')
    form = BlockForm

    inlines = [ParameterInline, ExampleInline]

    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'video', 'image', ('description', 'gen_description')],
        }),
        ('Documentation', {
            'fields': ['proxy', 'ext_doc', 'parent_cat', 'content'],
        }),
        ('Details', {
            'fields': ['syntax', 'return_value'],
            'classes': ['collapse-closed'],
        }),
        ('Tips', {
            'fields': ['tips', ],
            'classes': ['collapse-closed'],
        }),
    )

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2})},
    }


class MultiBlock(Block):
    class Meta:
        proxy = True


class MultiBlockAdmin(admin.ModelAdmin):
    list_display = ('parent_ide', 'title', 'syntax', 'parent_cat', 'ext_doc')
    list_editable = ('syntax', 'parent_cat', 'ext_doc')
    list_filter = ('parent_ide',)
    ordering = ('parent_ide', '_order')

    def get_changelist_form(self, request, **kwargs):
        return BlockDocForm

admin.site.register(Block, BlockAdmin)
admin.site.register(IDE, IDEAdmin)
admin.site.register(BlockDoc, BlockDocAdmin)
admin.site.register(MultiBlock, MultiBlockAdmin)
admin.site.register(Map, MapAdmin)

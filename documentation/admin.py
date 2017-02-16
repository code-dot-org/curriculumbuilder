from django.contrib import admin
from django.db import models
from django.forms import Textarea, ModelForm, TextInput
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin

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


class IDEAdmin(PageAdmin):
    model = IDE

    inlines = [CategoryInline, ]

    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'keywords', 'language', ('description', 'gen_description')],
        }),
        ('Documentation', {
            'fields': ['url', 'content'],
        }),
    )


class BlockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)

        if self.instance.parent:
            categories_queryset = Category.objects.filter(IDE=self.instance.parent.ide)
        else:
            categories_queryset = Category.objects.all()

        videos_queryset = Resource.objects.filter(type__iexact="video")

        self.fields['category'].queryset = categories_queryset
        self.fields['video'].queryset = videos_queryset


class BlockAdmin(PageAdmin):
    form = BlockForm

    inlines = [ParameterInline, ExampleInline]

    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'keywords', 'video', ('description', 'gen_description')],
        }),
        ('Documentation', {
            'fields': ['proxy', 'ext_doc', 'category', 'content'],
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


class MapAdmin(PageAdmin):
    model = Map

    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'keywords', 'content'],
        }),
    )


class BlockDocForm(ModelForm):
    class Meta:
        model = Block
        fields = ['IDE', 'title', 'syntax', 'category', 'ext_doc', 'proxy']
        ordering = ('IDE', '_order')
        widgets = {
            'syntax': Textarea(attrs={'cols': '10'}),
            'ext_doc': TextInput(attrs={'size': '10'})
        }


class BlockDoc(Block):
    class Meta:
        proxy = True


class BlockDocAdmin(admin.ModelAdmin):
    list_display = ('title', 'IDE', 'category')
    list_filter = ('IDE', 'category')
    ordering = ('IDE', '_order')
    form = BlockForm

    inlines = [ParameterInline, ExampleInline]

    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'keywords', 'video', ('description', 'gen_description')],
        }),
        ('Documentation', {
            'fields': ['proxy', 'ext_doc', 'category', 'content'],
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
    list_display = ('IDE', 'title', 'syntax', 'category', 'ext_doc')
    list_editable = ('syntax', 'category', 'ext_doc')
    list_filter = ('IDE',)
    ordering = ('IDE', '_order')

    def get_changelist_form(self, request, **kwargs):
        return BlockDocForm

admin.site.register(Block, BlockAdmin)
admin.site.register(IDE, IDEAdmin)
admin.site.register(BlockDoc, BlockDocAdmin)
admin.site.register(MultiBlock, MultiBlockAdmin)
admin.site.register(Map, MapAdmin)

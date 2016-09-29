from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea, ModelForm, BooleanField, ModelForm

from jackfrost.utils import build_page_for_obj

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin, AjaxSelectAdminTabularInline
from ajax_select.fields import autoselect_fields_check_can_add

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from mezzanine.core.fields import RichTextField, OrderField
from mezzanine.generic.fields import KeywordsField
from mezzanine_pagedown.widgets import PlainWidget

from lessons.models import Lesson, Objective, Prereq, Activity, Vocab, Resource, Annotation
from standards.models import Standard


def publish(modeladmin, request, queryset):
    for obj in queryset:
        print obj


class ObjectiveInline(TabularDynamicInlineAdmin):
    model = Objective
    fields = ["name", "_order"]
    verbose_name = "Objective"
    verbose_name_plural = "Objectives"
    extra = 3

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 100, 'style': 'width: 700px'})},
    }


class PrereqInline(StackedDynamicInlineAdmin):
    model = Prereq
    verbose_name = "Prerequisite"
    verbose_name_plural = "Prerequisites"
    extra = 3


class ActivityInline(StackedDynamicInlineAdmin):
    model = Activity
    verbose_name_plural = "Activities"
    extra = 5

    exclude = ['ancestor', ]


class ResourceInline(TabularDynamicInlineAdmin):
    model = Lesson.resources.through
    extra = 3

    sortable_field_name = "sort_value"
    readonly_fields = ('type', 'md_tag')
    verbose_name_plural = "Resources"

    def get_form(self, request, obj=None, **kwargs):
        form = super(ResourceInline, self).get_form(request, obj, **kwargs)
        autoselect_fields_check_can_add(form, self.model, request.user)
        return form

    def type(self, instance):
        return instance.resource.type

    def md_tag(self, instance):
        return instance.resource.md_tag()


class LessonForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(LessonForm, self).__init__(*args, **kwargs)

        standards_queryset = None

        try:
            curriculum = None
            if hasattr(self.instance.parent, 'chapter'):
                curriculum = self.instance.parent.chapter.curriculum
            elif hasattr(self.instance.parent, 'unit'):
                curriculum = self.instance.parent.unit.curriculum
            elif hasattr(self.instance.parent, 'curriculum'):
                curriculum = self.instance.parent.curriculum
            else:
                pass

            if curriculum.frameworks.count() > 0:
                standards_queryset = Standard.objects.filter(framework=curriculum.frameworks.all())
            else:
                standards_queryset = Standard.objects.all()

        except:
            standards_queryset = Standard.objects.all()

        if standards_queryset is None:
            standards_queryset = Standard.objects.all()
            
        self.fields['standards'].queryset = standards_queryset
        self.fields['anchor_standards'].queryset = standards_queryset


class LessonAdmin(PageAdmin, AjaxSelectAdmin):
    form = LessonForm

    actions = [publish]

    inlines = [ObjectiveInline, ResourceInline, ActivityInline]

    filter_horizontal = ('standards', 'anchor_standards', 'vocab', 'blocks')

    fieldsets = (
        (None, {
            'fields': ['title', ('status', 'login_required', 'duration', 'unplugged'), 'image', 'overview', 'keywords',
                       ('description', 'gen_description')],
        }),
        ('Purpose, Prep, & Questions', {
            'fields': ['cs_content', 'prep', 'questions'],
            'classes': ['collapse-closed'],
        }),
        ('Vocab & Blocks', {
            'fields': ['vocab', 'blocks'],
            'classes': ['collapse-closed'],
        }),
        ('Standards', {
            'fields': ['standards', 'anchor_standards'],
            'classes': ['collapse-closed'],
        }),
    )

    def get_queryset(self, request):
        return super(LessonAdmin, self).get_queryset(request).select_related('parent', 'page_ptr') \
            .prefetch_related('standards', 'anchor_standards',
                              'vocab', 'resources', 'activity_set')


'''
class MultiLessonForm(ModelForm):
  class Meta:
    model = Lesson
    fields = ['title', 'keywords']

  keywords = KeywordsField()

class MultiLesson(Lesson):
  class Meta:
    proxy = True

class MultiLessonAdmin(admin.ModelAdmin):
  list_display = ('curriculum', 'unit', 'title', 'keywords_string')
  list_editable = ('title', )
  list_filter = ('curriculum', 'unit')
  actions = [publish]

  def get_changelist_form(self, request, **kwargs):
    return MultiLessonForm
'''


class ResourceAdmin(AjaxSelectAdmin):
    model = Resource

    list_display = ('name', 'type', 'student', 'gd', 'url', 'dl_url')
    list_editable = ('type', 'student', 'gd', 'url', 'dl_url')


class VocabAdmin(ImportExportModelAdmin):
    model = Vocab

    list_display = ('word', 'simpleDef')
    list_editable = ('word', 'simpleDef')


class VocabResource(resources.ModelResource):
    class Meta:
        model = Vocab


admin.site.register(Lesson, LessonAdmin)
# admin.site.register(MultiLesson, MultiLessonAdmin)
admin.site.register(Lesson.resources.through)
admin.site.register(Prereq)
admin.site.register(Objective)
admin.site.register(Activity)
admin.site.register(Vocab, VocabAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Annotation)

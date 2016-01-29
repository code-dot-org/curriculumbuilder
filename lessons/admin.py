from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea, ModelForm, BooleanField

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin, AjaxSelectAdminTabularInline

from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from mezzanine.core.fields import RichTextField
from mezzanine_pagedown.widgets import PlainWidget

from lessons.models import Lesson, Objective, Prereq, Activity, Vocab, Resource
from standards.models import Standard

class ObjectiveInline(TabularDynamicInlineAdmin):
  model = Objective
  fields = ["name",]
  verbose_name = "Objective"
  verbose_name_plural = "Objectives"

  formfield_overrides = {
      models.CharField: {'widget': TextInput(attrs={'size':100, 'style':'width: 700px'})},
  }

class PrereqInline(StackedDynamicInlineAdmin):
  model = Prereq
  verbose_name = "Prerequisite"
  verbose_name_plural = "Prerequisites"

class ActivityInline(StackedDynamicInlineAdmin):
  model = Activity
  verbose_name_plural = "Activities"
  fields = ['name', 'content']
  class Meta:
    fields = ['name', 'content']

  formfield_overrides = {
    RichTextField: {'widget': PlainWidget(attrs={'rows':30})},
  }

class ResourceInline(TabularDynamicInlineAdmin):
  model = Lesson.resources.through

  class Meta:
    ordering = ['name']

  readonly_fields = ('type', 'student', 'gd', 'url', 'dl_url')
  verbose_name_plural = "Resources"

  def type(self, instance):
    return instance.resource.type

  def student(self, instance):
    return instance.resource.student

  def gd(self, instance):
    return instance.resource.gd

  def url(self, instance):
    return instance.resource.url

  def dl_url(self, instance):
    return instance.resource.dl_url

class LessonForm(ModelForm):

  class Meta:
    model = Lesson
    fields = ('status',)
    help_texts = {"status": "Draft documents will not be scooped during deployment."}

class LessonAdmin(PageAdmin, AjaxSelectAdmin):

  raw_id_fields = ('vocab', 'resources')

  form = LessonForm

  def get_queryset(self, request):
    qs = super(LessonAdmin, self).get_queryset(request)
    return qs.prefetch_related('activity_set', 'objective_set','prereq_set', 'standards',
                               'anchor_standards', 'resources', 'vocab')

  inlines = [ObjectiveInline, ResourceInline, ActivityInline]

  filter_horizontal = ('standards', 'vocab')

  fieldsets = (
    (None, {
      'fields': ['title', ('status', 'duration', 'unplugged'), 'overview',],
    }),
    ('CS Content, Materials & Prep', {
      'fields': ['cs_content', 'prep', 'vocab',],
      'classes': ['collapse-closed',],
    }),
    ('Standards', {
      'fields': ['standards'],
      'classes': ['collapse-closed',],
    }),
  )

class ResourceAdmin(AjaxSelectAdmin):
  model = Resource

  formfield_overrides = {
    models.CharField: {'widget': TextInput(attrs={'size':'10'})},
  }
  list_display = ('name', 'type', 'student', 'gd', 'url', 'dl_url')
  list_editable = ('type', 'student', 'gd', 'url', 'dl_url')

class VocabAdmin(AjaxSelectAdmin):
  pass

admin.site.register(Lesson, LessonAdmin)
admin.site.register(Prereq)
admin.site.register(Objective)
admin.site.register(Activity)
admin.site.register(Vocab, VocabAdmin)
admin.site.register(Resource, ResourceAdmin)
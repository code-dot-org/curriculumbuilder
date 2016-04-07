from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea, ModelForm, BooleanField, ModelForm

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin, AjaxSelectAdminTabularInline
from ajax_select.fields import autoselect_fields_check_can_add

from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from mezzanine.core.fields import RichTextField
from mezzanine_pagedown.widgets import PlainWidget

from lessons.models import Lesson, Objective, Prereq, Activity, Vocab, Resource, Annotation
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

  '''
  formfield_overrides = {
    RichTextField: {'widget': PlainWidget(attrs={'rows':30})},
  }
  '''

class ResourceInline(TabularDynamicInlineAdmin):
  model = Lesson.resources.through

  #raw_id_fields = ('resource',)

  class Meta:
    ordering = ['name']

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

class LessonAdmin(PageAdmin, AjaxSelectAdmin):
  #form = make_ajax_form(Lesson, {'vocab': 'vocab'})

  inlines = [ObjectiveInline, ResourceInline, ActivityInline]

  filter_horizontal = ('standards', 'vocab')

  fieldsets = (
    (None, {
      'fields': ['title', ('status', 'duration', 'unplugged'), 'overview', 'keywords'],
    }),
    ('Purpose & Prep', {
      'fields': ['cs_content', 'prep'],
      #'classes': ['collapse-closed',],
    }),
    ('Vocab', {
      'fields': ['vocab',],
      #'classes': ['collapse-closed'],
    }),
    ('Standards', {
      'fields': ['standards'],
      #'classes': ['collapse-closed',],
    }),
  )

class ResourceAdmin(AjaxSelectAdmin):
  model = Resource

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
admin.site.register(Annotation)
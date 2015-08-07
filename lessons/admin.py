from django import forms
from django.contrib import admin

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin, AjaxSelectAdminTabularInline

from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin

from lessons.models import Lesson, Objective, Prereq, Activity, Vocab, Resource
from standards.models import Standard

class ObjectiveInline(StackedDynamicInlineAdmin):
  model = Objective
  list_display = ['name', 'description']
  verbose_name = "Objective"
  verbose_name_plural = "Objectives"

class PrereqInline(StackedDynamicInlineAdmin):
  model = Prereq
  verbose_name = "Prerequisite"
  verbose_name_plural = "Prerequisites"

class ActivityInline(StackedDynamicInlineAdmin):
  model = Activity
  verbose_name_plural = "Activities"
  classes = ('collapse-open',)
  inline_classes = ('collapse-open',)

class LessonAdmin(PageAdmin, AjaxSelectAdmin):

  inlines = [ActivityInline, ObjectiveInline, PrereqInline]

  form = make_ajax_form(Lesson, {'vocab': 'vocab', 'resources': 'resources'})

  filter_horizontal = ('standards', 'anchor_standards')

  fieldsets = (
    (None, {
      'fields': ['title', ('duration', 'unplugged'), 'overview'],
    }),
    ('Standards', {
      'fields': ['anchor_standards', 'standards'],
    }),
    ('Vocab', {
      'fields': ['vocab'],
    }),
    ('Resources', {
      'fields': ['resources'],
    }),
    ('Meta', {
      'fields': ['cs_content', 'prep', 'keywords'],
    }),
  )
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Prereq)
admin.site.register(Objective)
admin.site.register(Activity)
admin.site.register(Vocab)
admin.site.register(Resource)
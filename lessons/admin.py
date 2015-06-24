from copy import deepcopy
from django.contrib import admin
from django import forms

from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin

from lessons.models import Lesson, Objective, Prereq, Activity, Vocab

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

class LessonAdmin(PageAdmin):
  inlines = [ActivityInline, ObjectiveInline, PrereqInline]

  filter_horizontal = ('standards','anchor_standards','vocab')

  fieldsets = (
    (None, {
      'fields': ['title', ('duration', 'unplugged'), 'overview']
    }),
    ('Standards', {
      'fields': ['anchor_standards', 'standards']
    }),
    ('Vocab', {
      'fields': ['vocab']
    }),
    ('Meta', {
      'fields': ['resources', 'slug', 'keywords'],
      'classes': ('collapse-closed',)
    }),
  )
  """
  fieldsets = (
    ('Meta', {
      'fields': ('title', 'duration', 'keywords')
    }),
    ('Body',{
      'fields': ('content', 'overview', 'summary')
    }),
  )
  """
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Prereq)
admin.site.register(Objective)
admin.site.register(Activity)
admin.site.register(Vocab)
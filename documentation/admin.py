from django.contrib import admin
from django.db import models
from django.forms import Textarea

from mezzanine.pages.admin import PageAdmin
from documentation.models import Block, IDE


class IDEAdmin(PageAdmin):
  model = IDE

  fieldsets = (
    (None, {
      'fields': ['title', 'slug', 'keywords', ('description', 'gen_description')],
    }),
    ('Documentation', {
      'fields': ['url', 'content'],
    }),
  )


class BlockAdmin(PageAdmin):
  model = Block

  fieldsets = (
    (None, {
      'fields': ['title', 'slug', 'keywords', ('description', 'gen_description')],
    }),
    ('Documentation', {
      'fields': ['code', 'content'],
    }),
  )

  formfield_overrides = {
      models.CharField: {'widget': Textarea(attrs={'rows': 2})},
  }

admin.site.register(Block, BlockAdmin)
admin.site.register(IDE, IDEAdmin)
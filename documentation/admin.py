from django.contrib import admin

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

admin.site.register(Block, BlockAdmin)
admin.site.register(IDE, IDEAdmin)
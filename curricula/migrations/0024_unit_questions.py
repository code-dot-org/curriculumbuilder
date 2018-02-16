# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0023_curriculum_canonical_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='questions',
            field=mezzanine.core.fields.RichTextField(help_text=b'Open questions or comments to add to all lessons in unit', null=True, verbose_name=b'Support Details', blank=True),
        ),
    ]

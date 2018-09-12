# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0038_lesson_opportunity_standards'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='resources',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, related_name='lessons', to='lessons.Resource', blank=True),
        ),
    ]

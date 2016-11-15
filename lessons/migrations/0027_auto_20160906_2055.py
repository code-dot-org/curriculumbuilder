# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sortedm2m.fields
from django.db import migrations, models
from sortedm2m.operations import AlterSortedManyToManyField


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0026_lesson_blocks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='duration',
            field=models.IntegerField(help_text=b'Week number within the unit (only use for first lesson of the week)',
                                      null=True, verbose_name=b'Week', blank=True),
        ),
        AlterSortedManyToManyField(
            model_name='lesson',
            name='resources',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='lessons.Resource', blank=True),
        ),
    ]

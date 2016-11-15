# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mezzanine.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('standards', '0004_auto_20160122_2141'),
        ('curricula', '0005_chapter_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='questions',
            field=mezzanine.core.fields.RichTextField(help_text=b'md list of big questions', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='chapter',
            name='understandings',
            field=models.ManyToManyField(to='standards.Category', blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import jsonfield.fields
import mezzanine.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0028_lesson_questions'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='stage',
            field=jsonfield.fields.JSONField(null=True, verbose_name=b'Code Studio stage', blank=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='cs_content',
            field=mezzanine.core.fields.RichTextField(
                help_text=b'Purpose of this lesson in progression and CS in general', null=True,
                verbose_name=b'Purpose', blank=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='duration',
            field=models.IntegerField(help_text=b'Week within the unit (only use for first lesson of the week)',
                                      null=True, verbose_name=b'Week', blank=True),
        ),
    ]

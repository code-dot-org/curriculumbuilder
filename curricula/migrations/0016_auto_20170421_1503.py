# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0015_unit_show_calendar'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='unit_template_override',
            field=models.CharField(help_text=b'Override default unit template, eg "curricula/pl_unit.html', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='unit',
            name='lesson_template_override',
            field=models.CharField(help_text=b'Override default lesson template, eg "curricula/pl_lesson.html', max_length=255, null=True, blank=True),
        ),
    ]

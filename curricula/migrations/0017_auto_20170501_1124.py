# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0016_auto_20170421_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='week_length',
            field=models.IntegerField(default=5, help_text=b'Controls the minimum lesson size in the pacing calendar.', null=True, verbose_name=b'Days in a Week', blank=True),
        ),
        migrations.AlterField(
            model_name='unit',
            name='lesson_template_override',
            field=models.CharField(help_text=b'Override default lesson template,eg curricula/pl_lesson.html', max_length=255, null=True, blank=True),
        ),
    ]

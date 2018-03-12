# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0034_activity_keywords_string'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='ancestor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='lessons.Activity', null=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='ancestor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='lessons.Lesson', null=True),
        ),
    ]

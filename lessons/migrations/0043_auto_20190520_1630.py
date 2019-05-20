# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0042_lesson_assessment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vocab',
            name='word',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0032_lesson_week'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='blocks',
            field=models.ManyToManyField(related_name='lessons', to='documentation.Block', blank=True),
        ),
    ]

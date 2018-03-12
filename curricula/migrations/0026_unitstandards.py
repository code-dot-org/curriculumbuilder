# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0036_lesson_short_title'),
        ('curricula', '0025_auto_20180222_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitStandards',
            fields=[
            ],
            options={
                'ordering': ('_order',),
                'proxy': True,
            },
            bases=('lessons.lesson',),
        ),
    ]

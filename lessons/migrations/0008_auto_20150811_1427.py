# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0007_lesson__old_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objective',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='prereq',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]

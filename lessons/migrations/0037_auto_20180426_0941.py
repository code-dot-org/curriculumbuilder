# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0036_lesson_short_title'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='activity',
            unique_together=set([('lesson', 'name')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0042_lesson_assessment'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vocab',
            unique_together=('word', 'mathy'),
        ),
    ]

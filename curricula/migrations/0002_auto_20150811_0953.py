# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('curricula', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitlesson',
            name='lesson',
        ),
        migrations.RemoveField(
            model_name='unitlesson',
            name='unit',
        ),
        migrations.DeleteModel(
            name='UnitLesson',
        ),
    ]

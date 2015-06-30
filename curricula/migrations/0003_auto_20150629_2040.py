# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0002_auto_20150629_2032'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='curriculum',
            options={'ordering': ('_order',), 'verbose_name_plural': 'curricula'},
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='name',
        ),
        migrations.RemoveField(
            model_name='unit',
            name='name',
        ),
    ]

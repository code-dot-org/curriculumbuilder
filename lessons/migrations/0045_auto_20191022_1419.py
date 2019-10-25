# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0044_auto_20191021_1519'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vocab',
            options={'ordering': ['word'], 'verbose_name_plural': 'vocab words', 'permissions': [('access_all_vocab', 'Can access all vocab')]},
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0004_auto_20150804_1511'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vocab',
            options={'ordering': ['word'], 'verbose_name_plural': 'vocab words'},
        ),
        migrations.AlterField(
            model_name='lesson',
            name='duration',
            field=models.IntegerField(null=True, verbose_name=b'Class Periods', blank=True),
        ),
        migrations.AlterField(
            model_name='vocab',
            name='detailDef',
            field=models.TextField(null=True, blank=True),
        ),
    ]

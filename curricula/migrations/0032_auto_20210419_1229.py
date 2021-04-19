# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0031_auto_20191023_1350'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unit',
            name='stage_name',
        ),
        migrations.AddField(
            model_name='unit',
            name='unit_name',
            field=models.CharField(db_column=b'stage_name', max_length=255, blank=True, help_text=b'Name of Code Studio script', null=True, verbose_name=b'Script'),
        ),
    ]

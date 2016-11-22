# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0011_unit_stage_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='stage_name',
            field=models.CharField(help_text=b'Name of Code Studio script', max_length=255, null=True, verbose_name=b'Script', blank=True),
        ),
    ]

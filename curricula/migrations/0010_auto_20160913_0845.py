# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('standards', '0004_auto_20160122_2141'),
        ('curricula', '0009_auto_20160907_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='frameworks',
            field=models.ManyToManyField(help_text=b'Standards frameworks aligned to', to='standards.Framework',
                                         blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='feedback_vars',
            field=models.CharField(help_text=b'Tuple of properties to use in feedback url', max_length=255, null=True,
                                   blank=True),
        ),
    ]

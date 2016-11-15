# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0012_auto_20160122_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='slug',
            field=models.CharField(max_length=255, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]

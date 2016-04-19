# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0022_auto_20160418_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='range_end',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='range_start',
            field=models.TextField(),
        ),
    ]

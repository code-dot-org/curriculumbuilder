# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documentation', '0002_auto_20160811_1545'),
        ('lessons', '0025_resource__order'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='blocks',
            field=models.ManyToManyField(to='documentation.Block', blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0019_auto_20180222_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='blocks',
            field=models.ManyToManyField(to='documentation.Block', blank=True),
        ),
    ]

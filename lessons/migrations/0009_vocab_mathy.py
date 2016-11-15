# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0008_auto_20150811_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocab',
            name='mathy',
            field=models.BooleanField(default=False),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0033_auto_20180111_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='keywords_string',
            field=models.CharField(max_length=500, editable=False, blank=True),
        ),
    ]

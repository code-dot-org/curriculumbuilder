# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0016_auto_20160315_0837'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='time',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]

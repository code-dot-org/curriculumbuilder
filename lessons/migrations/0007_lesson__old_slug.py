# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0006_auto_20150811_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='_old_slug',
            field=models.CharField(max_length=2000, null=True, verbose_name=b'old_slug', blank=True),
        ),
    ]

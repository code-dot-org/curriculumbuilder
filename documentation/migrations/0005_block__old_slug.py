# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0004_auto_20161121_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='_old_slug',
            field=models.CharField(max_length=2000, null=True, verbose_name=b'old_slug', blank=True),
        ),
    ]

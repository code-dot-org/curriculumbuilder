# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('curricula', '0006_auto_20160504_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='_old_slug',
            field=models.CharField(max_length=2000, null=True, verbose_name=b'old_slug', blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('curricula', '0002_auto_20150811_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='number',
            field=models.IntegerField(null=True, verbose_name=b'Number', blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0007_auto_20161122_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='ide',
            name='language',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]

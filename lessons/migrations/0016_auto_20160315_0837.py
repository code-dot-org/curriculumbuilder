# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0015_annotation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='uri',
            field=models.URLField(null=True, blank=True),
        ),
    ]

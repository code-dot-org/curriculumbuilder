# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0010_auto_20160913_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='stage_name',
            field=models.CharField(help_text=b'Name of Code Studio stage', max_length=255, null=True, blank=True),
        ),
    ]

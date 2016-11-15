# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('curricula', '0008_auto_20160907_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='feedback_vars',
            field=models.CharField(help_text=b'Vars to be used in feedback url', max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='feedback_url',
            field=models.URLField(help_text=b'URL to feedback form, using % operators', null=True, blank=True),
        ),
    ]

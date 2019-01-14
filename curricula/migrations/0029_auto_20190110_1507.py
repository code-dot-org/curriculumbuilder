# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0028_auto_20180711_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='forum_url',
            field=models.URLField(help_text=b'URL to forum, using % operators', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='unit',
            name='forum_vars',
            field=models.CharField(help_text=b'Tuple of properties to use in forum url', max_length=255, null=True, blank=True),
        ),
    ]

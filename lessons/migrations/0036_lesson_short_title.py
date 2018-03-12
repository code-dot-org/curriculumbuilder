# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0035_auto_20180222_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='short_title',
            field=models.CharField(help_text=b'Used where space is at a premium', max_length=64, null=True, verbose_name=b'Short Title (optional)', blank=True),
        ),
    ]

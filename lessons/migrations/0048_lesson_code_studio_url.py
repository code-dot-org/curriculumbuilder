# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0047_auto_20200402_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='code_studio_url',
            field=models.CharField(help_text=b'Link to the first puzzle of this lesson on code studio. Leave blank to auto-generate.', max_length=255, null=True, verbose_name=b'Custom Code Studio URL', blank=True),
        ),
    ]

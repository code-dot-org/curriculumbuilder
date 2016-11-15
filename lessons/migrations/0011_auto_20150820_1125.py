# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0010_auto_20150818_1003'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resource',
            options={'ordering': ['student', 'type']},
        ),
        migrations.AddField(
            model_name='resource',
            name='dl_url',
            field=models.URLField(help_text=b'Alternate download url', null=True, verbose_name=b'Download URL',
                                  blank=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='gd',
            field=models.BooleanField(default=False, verbose_name=b'Google Doc'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='student',
            field=models.BooleanField(default=False, verbose_name=b'Student Facing'),
        ),
    ]

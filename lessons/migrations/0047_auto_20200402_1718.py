# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0046_auto_20191023_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='creative_commons_image',
            field=models.CharField(default=b'img/creativeCommons-by-nc-sa.png', max_length=255, choices=[(b'img/creativeCommons-by-nc-sa.png', b'Creative Commons BY-NC-SA'), (b'img/creativeCommons-by-nc-nd.png', b'Creative Commons BY-NC-ND')]),
        ),
        migrations.AlterField(
            model_name='resource',
            name='gd',
            field=models.BooleanField(default=False, help_text=b'Only check this box for a google doc (Not google presentation, spreadsheet, etc)', verbose_name=b'Google Doc'),
        ),
    ]

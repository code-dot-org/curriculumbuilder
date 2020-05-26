# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0022_auto_20200512_0310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='example',
            name='app_display_type',
            field=models.CharField(default=b'codeFromCodeField', help_text=b'How the app and code fields for this example are rendered', max_length=255, choices=[(b'codeFromCodeField', b'Display app with code from code field above'), (b'embedAppWithCode', b'Embed app with code directly from code.org project')]),
        ),
    ]

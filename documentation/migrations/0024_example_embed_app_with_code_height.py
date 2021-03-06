# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0023_auto_20200514_0024'),
    ]

    operations = [
        migrations.AddField(
            model_name='example',
            name='embed_app_with_code_height',
            field=models.IntegerField(default=310, help_text=b'The height of the iframe, in pixels, to use when displaying an app with the "Embed app with code" display type', verbose_name=b'Embed app with code iframe height'),
        ),
    ]

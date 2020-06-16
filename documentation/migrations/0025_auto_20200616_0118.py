# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0024_example_embed_app_with_code_height'),
    ]

    operations = [
        migrations.AlterField(
            model_name='example',
            name='embed_app_with_code_height',
            field=models.IntegerField(default=310, help_text=b'The height of the iframe, in pixels, to use when displaying an app with the "Embed app with code"', verbose_name=b'Embed app with code iframe height'),
        ),
    ]

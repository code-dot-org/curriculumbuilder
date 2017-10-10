# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0010_map'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='image',
            field=models.FileField(null=True, upload_to=b'blocks/', blank=True),
        ),
        migrations.AddField(
            model_name='example',
            name='image',
            field=models.ImageField(null=True, upload_to=b'', blank=True),
        ),
    ]

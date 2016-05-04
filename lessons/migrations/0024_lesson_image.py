# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0023_auto_20160419_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='image',
            field=models.ImageField(upload_to=b'', null=True, verbose_name=b'Image', blank=True),
        ),
    ]

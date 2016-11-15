# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mezzanine.core.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0024_lesson_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='_order',
            field=mezzanine.core.fields.OrderField(null=True, verbose_name='Order'),
        ),
    ]

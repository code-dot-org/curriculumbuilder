# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0013_auto_20160225_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='comments_count',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0012_auto_20161122_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='unit_numbering',
            field=models.BooleanField(default=True),
        ),
    ]

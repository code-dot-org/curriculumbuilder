# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0005_block__old_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='proxy',
            field=models.ForeignKey(blank=True, to='documentation.Block', help_text=b'Existing block to pull documentation from', null=True),
        ),
    ]

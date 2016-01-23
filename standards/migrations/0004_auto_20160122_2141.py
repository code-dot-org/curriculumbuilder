# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('standards', '0003_auto_20150814_1340'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['framework', 'shortcode'], 'verbose_name_plural': 'categories'},
        ),
        migrations.AlterModelOptions(
            name='standard',
            options={'ordering': ['framework', 'category', 'slug']},
        ),
    ]

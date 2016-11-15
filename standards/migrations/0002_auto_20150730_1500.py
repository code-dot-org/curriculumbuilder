# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('standards', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='standard',
            options={'ordering': ['category__shortcode', 'shortcode']},
        ),
    ]

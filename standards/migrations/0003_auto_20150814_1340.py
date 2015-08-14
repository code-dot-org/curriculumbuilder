# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('standards', '0002_auto_20150730_1500'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='standard',
            options={'ordering': ['slug']},
        ),
    ]

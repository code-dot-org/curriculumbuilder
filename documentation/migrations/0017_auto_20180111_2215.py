# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0016_auto_20180111_2201'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='block',
            options={'ordering': ('_order',)},
        ),
    ]

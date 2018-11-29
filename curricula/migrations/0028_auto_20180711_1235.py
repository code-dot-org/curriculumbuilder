# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0027_auto_20180522_1155'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unitstandards',
            options={'ordering': ('_order',), 'verbose_name': 'Unit Standards', 'verbose_name_plural': 'Unit Standards'},
        ),
    ]

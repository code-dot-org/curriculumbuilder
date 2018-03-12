# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0021_auto_20180205_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='version',
            field=models.IntegerField(default=1, choices=[(0, b'Current'), (1, b'Next'), (2, b'Past')]),
        ),
    ]

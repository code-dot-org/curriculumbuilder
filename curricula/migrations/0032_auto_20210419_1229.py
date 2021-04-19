# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0031_auto_20191023_1350'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unit',
            old_name='stage_name',
            new_name='unit_name',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0021_example_example_app_display_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='example',
            old_name='example_app_display_type',
            new_name='app_display_type',
        ),
    ]

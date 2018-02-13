# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0012_auto_20171102_1338'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='block',
            options={'ordering': ['parent_ide', 'parent_cat']},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['parent_ide', '_order']},
        ),
        migrations.RenameField(
            model_name='block',
            old_name='category',
            new_name='parent_cat',
        ),
        migrations.RenameField(
            model_name='block',
            old_name='IDE',
            new_name='parent_ide',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='IDE',
            new_name='parent_ide',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0015_auto_20180111_2158'),
    ]

    operations = [
        migrations.RenameField(
            model_name='example',
            old_name='block',
            new_name='parent_block',
        ),
        migrations.RenameField(
            model_name='parameter',
            old_name='block',
            new_name='parent_block',
        ),
        migrations.AlterField(
            model_name='category',
            name='parent_ide',
            field=models.ForeignKey(related_name='categories', to='documentation.IDE'),
        ),
    ]

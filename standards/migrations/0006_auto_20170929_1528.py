# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('standards', '0005_auto_20170922_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standard',
            name='category',
            field=models.ForeignKey(related_name='standards', to='standards.Category'),
        ),
        migrations.AlterField(
            model_name='standard',
            name='framework',
            field=models.ForeignKey(related_name='standards', blank=True, to='standards.Framework', null=True),
        ),
    ]

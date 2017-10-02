# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('standards', '0004_auto_20160122_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='framework',
            field=models.ForeignKey(related_name='categories', blank=True, to='standards.Framework', null=True),
        ),
    ]

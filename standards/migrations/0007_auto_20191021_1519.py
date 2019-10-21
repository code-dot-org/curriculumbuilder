# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('standards', '0006_auto_20170929_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standard',
            name='gradeband',
            field=models.ForeignKey(related_name='standards', to='standards.GradeBand'),
        ),
    ]

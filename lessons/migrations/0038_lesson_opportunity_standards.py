# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('standards', '0006_auto_20170929_1528'),
        ('lessons', '0037_auto_20180426_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='opportunity_standards',
            field=models.ManyToManyField(help_text=b'Opportunities for content standards alignment', related_name='opportunities', to='standards.Standard', blank=True),
        ),
    ]

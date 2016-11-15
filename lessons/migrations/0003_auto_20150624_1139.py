# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0002_auto_20150623_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='anchor_standards',
            field=models.ManyToManyField(related_name='anchors', to='standards.Standard', blank=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='standards',
            field=models.ManyToManyField(to='standards.Standard', blank=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='vocab',
            field=models.ManyToManyField(to='lessons.Vocab', blank=True),
        ),
    ]

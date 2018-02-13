# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0013_auto_20180111_2122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='parent_cat',
            field=models.ForeignKey(related_name='blocks', blank=True, to='documentation.Category', null=True),
        ),
        migrations.AlterField(
            model_name='block',
            name='parent_ide',
            field=models.ForeignKey(related_name='blocks', blank=True, to='documentation.IDE', null=True),
        ),
        migrations.AlterField(
            model_name='block',
            name='video',
            field=models.ForeignKey(related_name='blocks', blank=True, to='lessons.Resource', null=True),
        ),
    ]

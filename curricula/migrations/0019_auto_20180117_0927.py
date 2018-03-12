# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0018_unit_disable_numbering'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='ancestor',
            field=models.ForeignKey(blank=True, to='curricula.Chapter', null=True),
        ),
        migrations.AddField(
            model_name='curriculum',
            name='ancestor',
            field=models.ForeignKey(blank=True, to='curricula.Curriculum', null=True),
        ),
        migrations.AddField(
            model_name='unit',
            name='ancestor',
            field=models.ForeignKey(blank=True, to='curricula.Unit', null=True),
        ),
    ]

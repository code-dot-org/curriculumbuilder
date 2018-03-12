# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0024_unit_questions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='ancestor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='curricula.Chapter', null=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='ancestor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='curricula.Curriculum', null=True),
        ),
        migrations.AlterField(
            model_name='curriculum',
            name='gradeband',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='standards.GradeBand', null=True),
        ),
        migrations.AlterField(
            model_name='unit',
            name='ancestor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='curricula.Unit', null=True),
        ),
    ]

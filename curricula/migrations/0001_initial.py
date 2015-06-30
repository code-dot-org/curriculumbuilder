# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('standards', '0001_initial'),
        ('lessons', '0003_auto_20150624_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Curriculum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('gradeband', models.ForeignKey(to='standards.GradeBand')),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('curriculum', models.ForeignKey(to='curricula.Curriculum')),
            ],
            options={
                'ordering': ('_order',),
            },
        ),
        migrations.CreateModel(
            name='UnitLesson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('lesson', models.ForeignKey(to='lessons.Lesson')),
                ('unit', models.ForeignKey(to='curricula.Unit')),
            ],
            options={
                'ordering': ('_order',),
            },
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mezzanine.core.fields
from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0003_auto_20150527_1555'),
        ('standards', '0001_initial'),
        ('lessons', '0003_auto_20150624_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Curriculum',
            fields=[
                ('page_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='pages.Page')),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
                ('gradeband', models.ForeignKey(to='standards.GradeBand')),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name_plural': 'curricula',
            },
            bases=('pages.page', models.Model),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('page_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='pages.Page')),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
                ('curriculum', models.ForeignKey(blank=True, to='curricula.Curriculum', null=True)),
            ],
            options={
                'ordering': ('_order',),
            },
            bases=('pages.page', models.Model),
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

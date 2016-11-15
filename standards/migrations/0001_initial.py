# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('shortcode', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('type', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
                'ordering': ['shortcode'],
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Framework',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
                ('website', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='GradeBand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('shortcode', models.CharField(max_length=50, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('grades', models.ManyToManyField(to='standards.Grade')),
            ],
        ),
        migrations.CreateModel(
            name='Standard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('shortcode', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('slug', models.CharField(max_length=50, null=True, blank=True)),
                ('category', models.ForeignKey(to='standards.Category')),
                ('framework', models.ForeignKey(blank=True, to='standards.Framework', null=True)),
                ('gradeband', models.ForeignKey(to='standards.GradeBand')),
            ],
            options={
                'ordering': ['shortcode'],
            },
        ),
        migrations.AddField(
            model_name='category',
            name='framework',
            field=models.ForeignKey(blank=True, to='standards.Framework', null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='standards.Category', null=True),
        ),
    ]

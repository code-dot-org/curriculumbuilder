# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0003_auto_20150624_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255, null=True, blank=True)),
                ('student', models.BooleanField(default=False)),
                ('url', models.URLField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='lesson',
            name='cs_content',
            field=mezzanine.core.fields.RichTextField(null=True, verbose_name=b'CS Content', blank=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='prep',
            field=mezzanine.core.fields.RichTextField(null=True, verbose_name=b'Materials and Prep', blank=True),
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='resources',
        ),
        migrations.AddField(
            model_name='lesson',
            name='resources',
            field=models.ManyToManyField(to='lessons.Resource', blank=True),
        ),
    ]

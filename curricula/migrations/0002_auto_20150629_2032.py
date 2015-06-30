# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20150527_1555'),
        ('curricula', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='curriculum',
            options={'ordering': ('_order',)},
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='description',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='id',
        ),
        migrations.RemoveField(
            model_name='unit',
            name='_order',
        ),
        migrations.RemoveField(
            model_name='unit',
            name='description',
        ),
        migrations.RemoveField(
            model_name='unit',
            name='id',
        ),
        migrations.AddField(
            model_name='curriculum',
            name='content',
            field=mezzanine.core.fields.RichTextField(default='', verbose_name='Content'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='curriculum',
            name='page_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default='', serialize=False, to='pages.Page'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unit',
            name='content',
            field=mezzanine.core.fields.RichTextField(default='', verbose_name='Content'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unit',
            name='page_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default='', serialize=False, to='pages.Page'),
            preserve_default=False,
        ),
    ]

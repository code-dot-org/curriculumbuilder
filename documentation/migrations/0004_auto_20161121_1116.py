# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0003_auto_20160818_0901'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('name', models.CharField(max_length=255)),
                ('color', models.CharField(max_length=255)),
                ('IDE', models.ForeignKey(to='documentation.IDE')),
            ],
            options={
                'ordering': ('_order',),
            },
        ),
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('code', mezzanine.core.fields.RichTextField()),
                ('description', models.TextField(null=True, blank=True)),
                ('app', models.URLField(help_text=b'Sharing link for example app', null=True, blank=True)),
            ],
            options={
                'ordering': ('_order',),
            },
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(help_text=b'Data type, capitalized', max_length=64, null=True, blank=True)),
                ('required', models.BooleanField(default=True)),
                ('description', mezzanine.core.fields.RichTextField()),
            ],
            options={
                'ordering': ('_order',),
            },
        ),
        migrations.AlterModelOptions(
            name='block',
            options={'ordering': ['IDE', 'category']},
        ),
        migrations.RemoveField(
            model_name='block',
            name='code',
        ),
        migrations.AddField(
            model_name='block',
            name='ext_doc',
            field=models.URLField(help_text=b'Link to external documentation', null=True, verbose_name=b'External Documentation', blank=True),
        ),
        migrations.AddField(
            model_name='block',
            name='return_value',
            field=models.CharField(help_text=b'Description of return value or alternate functionality', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='block',
            name='signature',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='block',
            name='syntax',
            field=mezzanine.core.fields.RichTextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='block',
            name='tips',
            field=mezzanine.core.fields.RichTextField(help_text=b'List of tips for using this block', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='parameter',
            name='block',
            field=models.ForeignKey(to='documentation.Block'),
        ),
        migrations.AddField(
            model_name='example',
            name='block',
            field=models.ForeignKey(to='documentation.Block'),
        ),
        migrations.AddField(
            model_name='block',
            name='category',
            field=models.ForeignKey(blank=True, to='documentation.Category', null=True),
        ),
    ]

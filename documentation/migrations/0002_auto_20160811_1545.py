# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mezzanine.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0003_auto_20150527_1555'),
        ('documentation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IDE',
            fields=[
                ('page_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='pages.Page')),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
                ('url', models.URLField()),
            ],
            options={
                'ordering': ('_order',),
            },
            bases=('pages.page', models.Model),
        ),
        migrations.AddField(
            model_name='block',
            name='IDE',
            field=models.ForeignKey(blank=True, to='documentation.IDE', null=True),
        ),
    ]

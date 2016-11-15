# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mezzanine.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0003_auto_20150527_1555'),
        ('curricula', '0003_unit_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('page_ptr',
                 models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False,
                                      to='pages.Page')),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
            ],
            options={
                'ordering': ('_order',),
            },
            bases=('pages.page', models.Model),
        ),
    ]

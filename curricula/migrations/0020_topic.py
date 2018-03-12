# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0019_auto_20180117_0927'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('name', models.CharField(max_length=255)),
                ('content', mezzanine.core.fields.RichTextField(verbose_name=b'Topic Content')),
                ('page', models.ForeignKey(to='pages.Page')),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name_plural': 'topics',
            },
        ),
    ]

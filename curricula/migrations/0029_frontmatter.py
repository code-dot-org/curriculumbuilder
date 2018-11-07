# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_auto_20161026_2025'),
        ('curricula', '0028_auto_20180711_1235'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrontMatter',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pages.Page')),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
                ('i18n_ready', models.BooleanField(default=False, help_text=b'Ready for internationalization')),
                ('ancestor', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='curricula.FrontMatter', null=True)),
                ('curriculum', models.ForeignKey(blank=True, to='curricula.Curriculum', null=True)),
            ],
            options={
                'ordering': ('_order',),
            },
            bases=('pages.page', models.Model),
        ),
    ]

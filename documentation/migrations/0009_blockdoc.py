# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0008_ide_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockDoc',
            fields=[
            ],
            options={
                'ordering': ('_order',),
                'proxy': True,
            },
            bases=('documentation.block',),
        ),
    ]

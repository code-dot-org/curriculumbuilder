# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0030_auto_20161128_1005'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiLesson',
            fields=[
            ],
            options={
                'ordering': ('_order',),
                'proxy': True,
            },
            bases=('lessons.lesson',),
        ),
        migrations.AddField(
            model_name='lesson',
            name='pacing_weight',
            field=models.DecimalField(decimal_places=1, default=1, max_digits=4, blank=True, help_text=b'Higher numbers take up more space pacing calendar', null=True, verbose_name=b'Pacing Weight'),
        ),
    ]

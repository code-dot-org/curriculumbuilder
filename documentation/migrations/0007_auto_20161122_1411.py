# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0029_auto_20160923_1041'),
        ('documentation', '0006_block_proxy'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiBlock',
            fields=[
            ],
            options={
                'ordering': ('_order',),
                'proxy': True,
            },
            bases=('documentation.block',),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['IDE', '_order']},
        ),
        migrations.AddField(
            model_name='block',
            name='video',
            field=models.ForeignKey(blank=True, to='lessons.Resource', null=True),
        ),
    ]

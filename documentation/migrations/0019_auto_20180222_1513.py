# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0018_auto_20180114_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='parent_cat',
            field=models.ForeignKey(related_name='blocks', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='documentation.Category', null=True),
        ),
        migrations.AlterField(
            model_name='block',
            name='proxy',
            field=models.ForeignKey(related_name='proxied', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='documentation.Block', help_text=b'Existing block to pull documentation from', null=True),
        ),
        migrations.AlterField(
            model_name='block',
            name='video',
            field=models.ForeignKey(related_name='blocks', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='lessons.Resource', null=True),
        ),
    ]

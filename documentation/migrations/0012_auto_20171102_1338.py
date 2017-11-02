# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0011_auto_20171006_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='parent_object',
            field=models.ForeignKey(related_name='object', blank=True, to='documentation.Block', help_text=b'Parent object for property or method', null=True),
        ),
        migrations.AlterField(
            model_name='block',
            name='proxy',
            field=models.ForeignKey(related_name='proxied', blank=True, to='documentation.Block', help_text=b'Existing block to pull documentation from', null=True),
        ),
    ]

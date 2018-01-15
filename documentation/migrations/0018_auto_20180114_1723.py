# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0017_auto_20180111_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='parent_object',
            field=models.ForeignKey(related_name='properties', blank=True, to='documentation.Block', help_text=b'Parent object for property or method', null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0014_auto_20180111_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='example',
            name='block',
            field=models.ForeignKey(related_name='examples', to='documentation.Block'),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='block',
            field=models.ForeignKey(related_name='parameters', to='documentation.Block'),
        ),
    ]

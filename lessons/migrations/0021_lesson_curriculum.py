# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0003_unit_number'),
        ('lessons', '0020_auto_20160418_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='curriculum',
            field=models.ForeignKey(blank=True, to='curricula.Curriculum', null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('curricula', '0004_chapter'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='number',
            field=models.IntegerField(null=True, verbose_name=b'Number', blank=True),
        ),
    ]

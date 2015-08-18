# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0009_vocab_mathy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='name',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]

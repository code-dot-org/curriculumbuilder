# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0022_curriculum_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='canonical_slug',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0013_curriculum_unit_numbering'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='support_script',
            field=models.BooleanField(default=False, help_text=b'Link to support script in Code Studio?'),
        ),
    ]

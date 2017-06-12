# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0017_auto_20170501_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='disable_numbering',
            field=models.BooleanField(default=False, help_text=b'Override to disable unit numbering'),
        ),
    ]

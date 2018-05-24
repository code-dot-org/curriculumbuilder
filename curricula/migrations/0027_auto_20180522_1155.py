# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0026_unitstandards'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='i18n_ready',
            field=models.BooleanField(default=False, help_text=b'Ready for internationalization'),
        ),
    ]

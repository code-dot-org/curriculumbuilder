# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0014_curriculum_support_script'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='show_calendar',
            field=models.BooleanField(default=False, help_text=b'Show pacing guide calendar?', verbose_name=b'Show Calendar'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('curricula', '0007_chapter__old_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='auto_forum',
            field=models.BooleanField(default=False, help_text=b'Automatically generate forum links?'),
        ),
        migrations.AddField(
            model_name='curriculum',
            name='display_questions',
            field=models.BooleanField(default=False, help_text=b'Display open questions and feedback form?'),
        ),
        migrations.AddField(
            model_name='curriculum',
            name='feedback_url',
            field=models.URLField(help_text=b'URL to feedback form', null=True, blank=True),
        ),
    ]

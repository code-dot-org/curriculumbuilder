# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0040_resource_force_i18n'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='force_i18n',
            field=models.BooleanField(default=False, help_text=b'\n        By default, only Resources that have been associated with a Lesson that\n        is itself being internationalized will be internationalized. However, we\n        occasionally want to be able to include Resources inline in markdown,\n        and those Resources will not be automatically synced.\n\n        Use this flag if for that or any other reason you would like to force a\n        Resource to be synced.\n    ', verbose_name=b'Force I18n'),
        ),
    ]

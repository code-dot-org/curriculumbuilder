# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0029_auto_20160923_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='questions',
            field=mezzanine.core.fields.RichTextField(help_text=b'Open questions or comments about this lesson', null=True, verbose_name=b'Support Details', blank=True),
        ),
    ]

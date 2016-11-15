# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0027_auto_20160906_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='questions',
            field=mezzanine.core.fields.RichTextField(help_text=b'Open Questions About this Lesson', null=True, verbose_name=b'Open Questions', blank=True),
        ),
    ]

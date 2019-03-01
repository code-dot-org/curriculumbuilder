# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0041_auto_20190110_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='assessment',
            field=mezzanine.core.fields.RichTextField(help_text=b'Parts of the lesson that can be assessed for students understaning', null=True, verbose_name=b'Assessment Opportunities', blank=True),
        ),
    ]

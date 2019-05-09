# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0029_auto_20190110_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='assessment_commentary',
            field=mezzanine.core.fields.RichTextField(help_text=b'How this course approaches assessment', null=True, verbose_name=b'Assessment Commentary', blank=True),
        ),
        migrations.AddField(
            model_name='unit',
            name='assessment_commentary',
            field=mezzanine.core.fields.RichTextField(help_text=b'How this unit approaches assessment', null=True, verbose_name=b'Assessment Commentary', blank=True),
        ),
    ]

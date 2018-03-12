# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0020_topic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='page',
            field=models.ForeignKey(related_name='topics', to='pages.Page'),
        ),
    ]

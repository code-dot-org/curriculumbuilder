# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentation', '0002_auto_20160811_1545'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='block',
            options={'ordering': ['IDE', 'title']},
        ),
    ]

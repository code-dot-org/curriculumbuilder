# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('curricula', '0030_auto_20190508_1556'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'ordering': ('_order',), 'permissions': [('access_all_chapters', 'Can access all chapters')]},
        ),
        migrations.AlterModelOptions(
            name='curriculum',
            options={'ordering': ('_order',), 'verbose_name_plural': 'curricula', 'permissions': [('access_all_curricula', 'Can access all curricula')]},
        ),
        migrations.AlterModelOptions(
            name='unit',
            options={'ordering': ('_order',), 'permissions': [('access_all_units', 'Can access all units')]},
        ),
        migrations.AddField(
            model_name='chapter',
            name='user',
            field=models.ForeignKey(related_name='chapters', default=1, verbose_name='Author', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='curriculum',
            name='user',
            field=models.ForeignKey(related_name='curriculums', default=1, verbose_name='Author', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unit',
            name='user',
            field=models.ForeignKey(related_name='units', default=1, verbose_name='Author', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]

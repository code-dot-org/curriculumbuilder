# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lessons', '0045_auto_20191022_1419'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ('_order',), 'verbose_name_plural': 'activities', 'permissions': [('access_all_activities', 'Can access all activities')]},
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['number'], 'permissions': [('access_all_lessons', 'Can access all lessons')]},
        ),
        migrations.AlterModelOptions(
            name='objective',
            options={'ordering': ('_order',), 'permissions': [('access_all_objectives', 'Can access all objectives')]},
        ),
        migrations.AlterModelOptions(
            name='resource',
            options={'ordering': ['name'], 'permissions': [('access_all_resources', 'Can access all resources')]},
        ),
        migrations.AddField(
            model_name='activity',
            name='user',
            field=models.ForeignKey(related_name='activitys', default=1, verbose_name='Author', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lesson',
            name='user',
            field=models.ForeignKey(related_name='lessons', default=1, verbose_name='Author', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='objective',
            name='user',
            field=models.ForeignKey(related_name='objectives', default=1, verbose_name='Author', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='resource',
            name='user',
            field=models.ForeignKey(related_name='resources', default=1, verbose_name='Author', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]

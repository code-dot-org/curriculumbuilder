# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('generic', '0002_auto_20141227_0224'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lessons', '0043_auto_20190520_1630'),
    ]

    operations = [
        migrations.CreateModel(
            name='I18nKeyword',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('generic.keyword', models.Model),
        ),
        migrations.AddField(
            model_name='vocab',
            name='user',
            field=models.ForeignKey(related_name='vocabs', default=1, verbose_name='Author', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]

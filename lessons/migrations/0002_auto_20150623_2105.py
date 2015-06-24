# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vocab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word', models.CharField(max_length=255)),
                ('simpleDef', models.TextField()),
                ('detailDef', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='lesson',
            name='vocab',
            field=models.ManyToManyField(to='lessons.Vocab'),
        ),
    ]

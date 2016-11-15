# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lessons', '0014_lesson_comments_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('annotator_schema_version', models.CharField(max_length=8, blank=True)),
                ('text', models.TextField(blank=True)),
                ('quote', models.TextField()),
                ('uri', models.URLField(blank=True)),
                ('range_start', models.CharField(max_length=50)),
                ('range_end', models.CharField(max_length=50)),
                ('range_startOffset', models.BigIntegerField()),
                ('range_endOffset', models.BigIntegerField()),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(editable=False)),
                ('lesson', models.ForeignKey(related_name='annotation_parent_lesson_relation', to='lessons.Lesson')),
                ('owner', models.ForeignKey(related_name='annotation_creator_relation', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

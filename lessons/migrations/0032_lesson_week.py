# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def move_week(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Lesson = apps.get_model('lessons', 'Lesson')
    for lesson in Lesson.objects.all():
        lesson.week = lesson.duration
        lesson.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0031_auto_20170417_2230'),
    ]

    operations = [
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE',
                          reverse_sql=migrations.RunSQL.noop),
        migrations.AddField(
            model_name='lesson',
            name='week',
            field=models.IntegerField(help_text=b'Week within the unit (only use for first lesson of the week)',
                                      null=True, verbose_name=b'Week', blank=True),
        ),
        migrations.RunPython(move_week),
        migrations.AlterField(
            model_name='lesson',
            name='duration',
            field=models.CharField(help_text=b'Duration of lesson', max_length=255, null=True, verbose_name=b'Duration', blank=True),
        ),
        migrations.RunSQL(migrations.RunSQL.noop,
                          reverse_sql='SET CONSTRAINTS ALL IMMEDIATE'),
    ]

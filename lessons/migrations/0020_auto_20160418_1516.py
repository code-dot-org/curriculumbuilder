# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_numbers(apps, schema_editor):
    # Resave all lessons so they get their units updated
    Lesson = apps.get_model("lessons", "Lesson")
    for lesson in Lesson.objects.all():
        lesson.save()


class Migration(migrations.Migration):
    dependencies = [
        ('lessons', '0019_auto_20160418_1420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['_order']},
        ),
        migrations.AddField(
            model_name='lesson',
            name='number',
            field=models.IntegerField(null=True, verbose_name=b'Number', blank=True),
        ),
        migrations.RunPython(update_numbers)
    ]

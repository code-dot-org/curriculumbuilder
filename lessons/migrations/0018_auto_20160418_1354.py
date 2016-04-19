# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mezzanine.core.fields

def update_units(apps, schema_editor):
    # Resave all lessons so they get their units updated
    Lesson = apps.get_model("lessons", "Lesson")
    for lesson in Lesson.objects.all():
        lesson.save()

class Migration(migrations.Migration):

    dependencies = [
        ('curricula', '0002_auto_20150811_0953'),
        ('lessons', '0017_activity_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='unit',
            field=models.ForeignKey(blank=True, to='curricula.Unit', null=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='anchor_standards',
            field=models.ManyToManyField(help_text=b'1 - 3 key standards this lesson focuses on', related_name='anchors', to='standards.Standard', blank=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='cs_content',
            field=mezzanine.core.fields.RichTextField(help_text=b'Purpose of this lesson in connection to greater CS concepts and its role in the progression', null=True, verbose_name=b'Purpose', blank=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='duration',
            field=models.IntegerField(help_text=b'Week number within the unit', null=True, verbose_name=b'Week', blank=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='prep',
            field=mezzanine.core.fields.RichTextField(help_text=b'ToDos for the teacher to prep this lesson', null=True, verbose_name=b'Preparation', blank=True),
        ),
        #migrations.RunPython(update_units)
    ]

# -*- coding: utf-8 -*-

"""Tests for the Standards package"""

import csv
import io

from django.test import TestCase
from django.core.urlresolvers import reverse

from curricula.models import Curriculum, Unit
from lessons.models import Lesson
from standards.models import Category, GradeBand, Framework

class StandardsViewsTestCase(TestCase):
    """Tests for standards/views.py"""
    def setUp(self):
        # This is admittedly an absurd amount of setup to have to do for such a
        # simple test suite, but until we have some kind of test factory
        # library this is what we have to do.
        # TODO simplify this if we ever set up a test factory.
        self.test_curriculum = Curriculum.objects.create(title="Test Curriculum")
        self.test_unit = Unit.objects.create(title="Test Unit", parent=self.test_curriculum)
        self.test_lesson = Lesson.objects.create(title="Test Lesson", parent=self.test_unit)
        self.test_framework = Framework.objects.create(
            name="Test Framework",
            slug="test_framework",
            description="This is a framework just for the test",
            website="http://example.com"
        )
        self.test_category = Category.objects.create(
            name="Test Category",
            shortcode="tc",
            framework=self.test_framework
        )
        self.test_gradeband = GradeBand.objects.create(name="Test GradeBand")
        self.test_lesson.standards.create(
            name="Test Standard",
            shortcode="ts",
            category=self.test_category,
            gradeband=self.test_gradeband
        )

    def test_by_curriculum_csv(self, *args):
        """CSVs generated from Curriculum models should contain the relevant data"""

        response = self.client.get(
            reverse('curriculum:by_curriculum_csv', args=[self.test_curriculum.slug])
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        body = list(csv.reader(io.StringIO(content)))

        self.assertEqual(len(body), 2)
        self.assertEqual(body[0], [
            'curriculum', 'unit', 'lesson #', 'lesson name',
            'standard framework', 'standard', 'cross curricular opportunity'
        ])
        self.assertEqual(body[1], [
            'test-curriculum', 'test-unit', 'lesson 1', 'Test Lesson',
            'test_framework', 'ts', 'False'
        ])

    def test_by_curriculum_csv_unicode(self, *args):
        """CSVs generated from Curriculum models should support unicode content"""

        self.test_lesson.title = u"Lección de Prueba con Unicodé"
        self.test_lesson.save()
        response = self.client.get(
            reverse('curriculum:by_curriculum_csv', args=[self.test_curriculum.slug])
        )
        self.assertEqual(response.status_code, 200)

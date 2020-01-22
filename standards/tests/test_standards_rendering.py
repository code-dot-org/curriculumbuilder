from django.test import TestCase

from curricula.factories import CurriculumFactory, UnitFactory
from lessons.factories import LessonFactory

from standards.factories import StandardFactory, FrameworkFactory, CategoryFactory


class StandardsRenderingTestCase(TestCase):
    def setUp(self):
        self.test_curriculum = CurriculumFactory(slug="test-curriculum")
        self.test_unit = UnitFactory(parent=self.test_curriculum, slug="test-unit", unit_name="test-unit-name")

        self.test_framework = FrameworkFactory()
        self.test_category = CategoryFactory()
        self.test_standard = StandardFactory(name="Test Standard", category=self.test_category, framework=self.test_framework)

        self.test_lesson = LessonFactory(parent=self.test_unit)
        self.test_lesson.standards.add(self.test_standard)

    def test_render_course_standards_page(self):
        response = self.client.get('/test-curriculum/standards/')
        self.assertEqual(response.status_code, 200)
        # Standards Alignment header only shows if there are standards
        self.assertIn('Standards Alignment', response.content)
        self.assertIn('Test Standard', response.content)

    def test_render_lesson_includes_standard(self):
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)
        # Standards Alignment header only shows if there are standards
        self.assertIn('Standards Alignment', response.content)
        self.assertIn('Test Standard', response.content)

    def test_standards_metadata_for_unit(self):
        response = self.client.get('/metadata/test-unit-name/standards.json')
        self.assertEqual(response.status_code, 200)

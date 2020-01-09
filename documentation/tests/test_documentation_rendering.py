from django.test import TestCase

from curricula.factories import CurriculumFactory, UnitFactory
from lessons.factories import LessonFactory

from documentation.factories import IDEFactory, BlockFactory, CategoryFactory, MapFactory


class DocumentationRenderingTestCase(TestCase):
    def setUp(self):
        self.myIDE = IDEFactory(slug="mylab")
        self.myCategory = CategoryFactory(name="My Category", parent_ide=self.myIDE)
        self.myBlock = BlockFactory(slug="myBlock", title="My Block", parent_ide=self.myIDE, parent=self.myIDE, parent_cat=self.myCategory)

        self.test_curriculum = CurriculumFactory(slug="test-curriculum")
        self.test_unit = UnitFactory(parent=self.test_curriculum, slug="test-unit")

        self.test_lesson = LessonFactory(title="My Lesson", parent=self.test_unit)
        self.test_lesson.blocks.add(self.myBlock)

        self.myConcept = MapFactory(slug="concepts", title="Concepts")
        self.myMap = MapFactory(slug="concepts/myMap", title="My Map", parent=self.myConcept)

    def test_render_course_blocks_page(self):
        response = self.client.get('/test-curriculum/code/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('My Lesson', response.content)
        self.assertIn('My Block', response.content)

    def test_render_lesson_includes_blocks(self):
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Introduced Code', response.content)
        self.assertIn('My Block', response.content)

    def test_render_ide_blocks(self):
        response = self.client.get('/documentation/mylab/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Try it out', response.content)
        self.assertIn('My Category', response.content)
        self.assertIn('My Block', response.content)
        response2 = self.client.get('/documentation/mylab/myBlock/')
        self.assertEqual(response2.status_code, 200)
        self.assertIn('My Category', response2.content)
        self.assertIn('My Block', response2.content)
        response = self.client.get('/docs/mylab/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Try it out', response.content)
        self.assertIn('My Category', response2.content)
        self.assertIn('My Block', response2.content)
        response2 = self.client.get('/docs/mylab/myBlock/')
        self.assertEqual(response2.status_code, 200)
        self.assertIn('My Category', response2.content)
        self.assertIn('My Block', response2.content)

    def test_render_maps(self):
        response = self.client.get('/documentation/concepts/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Concepts', response.content)
        response2 = self.client.get('/documentation/concepts/myMap/')
        self.assertEqual(response2.status_code, 200)
        self.assertIn('My Map', response2.content)
        self.assertIn('Concepts', response2.content)
        response = self.client.get('/docs/concepts/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Concepts', response.content)
        response2 = self.client.get('/docs/concepts/myMap/')
        self.assertEqual(response2.status_code, 200)
        self.assertIn('My Map', response2.content)
        self.assertIn('Concepts', response2.content)
from django.test import TestCase

from curricula.factories import CurriculumFactory, UnitFactory
from lessons.factories import LessonFactory

from documentation.factories import IDEFactory, BlockFactory, CategoryFactory


class DocumentationRenderingTestCase(TestCase):
    def setUp(self):
        self.myIDE = IDEFactory(slug="mylab")
        self.myCategory = CategoryFactory(name="myCategory", parent_ide=self.myIDE)
        self.myBlock = BlockFactory(slug="myBlock", title="myBlock", parent_ide=self.myIDE, parent=self.myIDE, parent_cat=self.myCategory)

        self.test_curriculum = CurriculumFactory(slug="test-curriculum")
        self.test_unit = UnitFactory(parent=self.test_curriculum, slug="test-unit")

        self.test_lesson = LessonFactory(title="My Lesson", parent=self.test_unit)
        self.test_lesson.blocks.add(self.myBlock)

    def test_render_course_blocks_page(self):
        response = self.client.get('/test-curriculum/code/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('My Lesson', response.content)
        self.assertIn('myBlock', response.content)

    def test_render_lesson_includes_blocks(self):
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Introduced Code', response.content)
        self.assertIn('myBlock', response.content)

    def test_render_ide_blocks(self):
        response = self.client.get('/documentation/mylab/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Try it out', response.content)
        self.assertIn('myCategory', response.content)
        self.assertIn('myBlock', response.content)
        response2 = self.client.get('/documentation/mylab/myBlock/')
        self.assertEqual(response2.status_code, 200)
        self.assertIn('myCategory', response2.content)
        self.assertIn('myBlock', response2.content)

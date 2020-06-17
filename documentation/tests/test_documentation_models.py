from django.test import TestCase

from documentation.factories import MapFactory, IDEFactory, BlockFactory
from documentation.models import Example

class DocumentationModelsTestCase(TestCase):

    def setUp(self):
        self.myMap = MapFactory(title='my concept parent', slug='concepts/myConcept')
        self.myChildMap = MapFactory(title='my concept child', slug='concepts/myConcept/childConcept', parent=self.myMap)

        self.myIDE = IDEFactory(title='Applab', slug='applab')
        self.myBlock = BlockFactory(title='onEvent Block', slug='onEvent', parent_ide=self.myIDE, parent=self.myIDE)

    def test_get_published_url(self):
        result = self.myMap.get_published_url()
        self.assertEqual(result, '//studio.code.org/docs/concepts/myConcept/')
        result1 = self.myIDE.get_published_url()
        self.assertEqual(result1, '//studio.code.org/docs/applab/')
        result2 = self.myBlock.get_published_url()
        self.assertEqual(result2, '//studio.code.org/docs/applab/onEvent/')

    def test_jackfrost_url(self):
        result = self.myMap.jackfrost_urls()
        self.assertEqual(result, ['/documentation/concepts/myConcept/','/docs/concepts/myConcept/'])
        result1 = self.myIDE.jackfrost_urls()
        self.assertEqual(result1, ['/documentation/applab/', '/docs/applab/'])
        result2 = self.myBlock.jackfrost_urls()
        self.assertEqual(result2, ['/documentation/applab/onEvent/', '/documentation/applab/onEvent/embed/', '/docs/applab/onEvent/', '/docs/applab/onEvent/embed/'])

    def test_example_embed_app_with_code(self):
        example = Example(app_display_type=Example.EMBED_APP_WITH_CODE, app='www.testapps.org/appwith-specialcharacter')
        assert example.get_embed_app_and_code() == 'www.testapps.org/appwith-specialcharacter/embed_app_and_code'
        assert example.embed_app_with_code_height == 310

    def test_example_embed_app(self):
        example = Example(app = "http://studio.code.org/projects/spritelab/REKsWyJXYOCJtYWhcBxErg")
        assert example.get_embed_app() == "https://studio.code.org/projects/spritelab/REKsWyJXYOCJtYWhcBxErg/embed"

    def test_example_default_app_display_type(self):
        example = Example()
        assert example.app_display_type ==  Example.CODE_FROM_CODE_FIELD

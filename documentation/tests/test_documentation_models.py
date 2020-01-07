from django.test import TestCase

from documentation.factories import MapFactory, IDEFactory, BlockFactory

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

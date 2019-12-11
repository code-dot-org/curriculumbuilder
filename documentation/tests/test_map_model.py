from django.test import TestCase

from documentation.factories import MapFactory

from documentation.templatetags.documentation_extras import get_absolute_url_for_host

class MapModelTestCase(TestCase):

    def setUp(self):
        self.myMap = MapFactory(title='my concept parent', slug='concepts/myConcept')
        self.myChildMap = MapFactory(title='my concept child', slug='concepts/myConcept/childConcept', parent=self.myMap)

    def test_get_children(self):
        self.assertIn(self.myChildMap, self.myMap.get_children())

    def test_get_absolute_url_for_host(self):
        result = get_absolute_url_for_host(self.myMap, 'curriculum.code.org')
        self.assertEqual(result, '/documentation/concepts/myConcept/')
        result2 = get_absolute_url_for_host(self.myMap, 'studio.code.org')
        self.assertEqual(result2, '/docs/concepts/myConcept/')

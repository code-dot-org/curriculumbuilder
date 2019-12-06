from django.test import TestCase

from documentation.factories import MapFactory

# Tests for admin pages in lessons/admin.py
class MapModelTestCase(TestCase):

    def setUp(self):
        self.myMap = MapFactory(title='my concept parent', slug='concepts/myConcept')
        self.myChildMap = MapFactory(title='my concept child', slug='concepts/myConcept/childConcept', parent=self.myMap)

    def test_get_children(self):
        self.assertIn(self.myChildMap, self.myMap.get_children())

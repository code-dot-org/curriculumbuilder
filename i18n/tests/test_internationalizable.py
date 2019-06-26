from unittest2 import TestCase

from django.core.cache import cache
from django.db import models
from django.utils import translation

from i18n.models import Internationalizable

class TestModel(Internationalizable):
    """
    Minimal implementation of a Django model that supports internationalization
    """
    title = models.CharField(max_length=255)
    description = models.TextField()

    @classmethod
    def internationalizable_fields(cls):
        return ['title', 'description']

class InternationalizableTestCase(TestCase):
    """
    Basic tests for the Internationalizable abstract model
    """
    def setUp(self):
        TestModel(title="Test Title", description="Test Description").save()

    def test_gather_strings(self):
        """
        Test the ability to gather all source strings for a model into a single
        dict which can be serialized to JSON and uploaded to crowdin
        """
        strings = TestModel.gather_strings()
        self.assertEqual(strings, {
            "1": {
                "description": u"Test Description",
                "title": u"Test Title"
            }
        })

    def test_translate_to(self):
        """
        Test the ability to load translations from crowdin into an instance of
        a model
        """
        translation.activate('es-mx')
        cache.set("translations/es_MX/LC_MESSAGES/TestModel.json", {
            "1": {
                "description": u"Translated Description",
                "title": u"Translated Title"
            }
        })
        test_instance = TestModel.objects.get(pk=1)
        self.assertEqual(test_instance.title, "Translated Title")
        self.assertEqual(test_instance.description, "Translated Description")

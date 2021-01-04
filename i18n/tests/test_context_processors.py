"""
Tests for the custom i18n context processors
"""
from django.test import TestCase


class CurrentPathWithoutLanguageContextProcessorTests(TestCase):
    """
    Tests for the ``i18n.context_processors.current_path_without_language`` processor.
    """

    def test_standard_url(self):
        """
        Test that we don't alter a url without a language prefix
        """
        url = '/hoc/plugged/'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.context["request_path"], "/en-us/hoc/plugged/")
        self.assertEqual(response.context["CURRENT_PATH_WITHOUT_LANGUAGE"], "/hoc/plugged/")

    def test_english_url(self):
        """
        Test that we do alter a url which explicitly specifies english
        """
        url = '/en-us/hoc/plugged/'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.context["request_path"], "/en-us/hoc/plugged/")
        self.assertEqual(response.context["CURRENT_PATH_WITHOUT_LANGUAGE"], "/hoc/plugged/")

    def test_nonenglish_url(self):
        """
        Test that we do alter a url which explicitly specifies a nonenglish language
        """
        url = '/es-mx/hoc/plugged/'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.context["request_path"], "/es-mx/hoc/plugged/")
        self.assertEqual(response.context["CURRENT_PATH_WITHOUT_LANGUAGE"], "/hoc/plugged/")

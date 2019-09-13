from django.test import TestCase

from mezzanine.core.templatetags.mezzanine_tags import richtext_filters

class IframeDomainRestrictionTestCase(TestCase):
    """
    Test the RICHTEXT_ALLOWED_ATTRIBUTES logic that will only allow iframes to
    render certain domains
    """

    def test_allow_google_doc_iframes(self):
        richtext = '<iframe src="http://docs.google.com"></iframe>'
        self.assertEqual(richtext, richtext_filters(richtext))

    def test_reject_other_iframes(self):
        # Will reject non-google domains
        self.assertEqual('<iframe></iframe>',
                         richtext_filters('<iframe src="http://example.com"></iframe>'))

        # Will reject incomplete urls
        self.assertEqual('<iframe></iframe>',
                         richtext_filters('<iframe src="docs.google.com"></iframe>'))

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

from django.test import TestCase

from mezzanine.core.templatetags.mezzanine_tags import richtext_filters

class RichtextTestCase(TestCase):
    """
    Test our markdown rendering procedures
    """

    def test_disallow_object_tag(self):
        """
        we want to prevent translators from adding translations that embed unwanted content via
        object tags, so we disallow the use of those tags in markdown sitewide.
        """
        richtext = "<object type=\"application/pdf\" data=\"/media/examples/In-CC0.pdf\" width=\"250\" height=\"200\"></object>"
        self.assertEqual("<p></p>", richtext_filters(richtext))

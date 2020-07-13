# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from mezzanine.core.templatetags.mezzanine_tags import richtext_filters
from lessons.models import Resource


class ResourceLinksTestCase(TestCase):
    """
    Test our custom "resourcelinks" markdown plugin
    """
    def setUp(self):
        # For some reason, Resources need an associated User. So, create one.
        self.test_user, _created = User.objects.get_or_create(
            username="username",
            password="password"
        )

    def tearDown(self):
        self.test_user.delete()

    def test_rendering_basic_resource_link(self):
        Resource(name="name", type="type", slug="slug", url="url", user=self.test_user).save()
        markdown = "[r slug]"
        expected = '<p><a class="resource" href="url" target="_blank">name - type</a></p>'
        self.assertEqual(expected, richtext_filters(markdown))

    def test_rendering_resource_link_with_unicode(self):
        Resource(name=u"náme", type=u"typê", slug=u"slüg", url="url", user=self.test_user).save()
        markdown = u"[r slüg]"
        expected = u'<p><a class="resource" href="url" target="_blank">náme - typê</a></p>'
        self.assertEqual(expected, richtext_filters(markdown))

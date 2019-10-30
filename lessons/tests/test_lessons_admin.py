from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site

from mezzanine.core.models import SitePermission

from curricula.factories import UserFactory


# Tests for admin pages in lessons/admin.py
class LessonsAdminTestCase(TestCase):

    def setUp(self):
        user = UserFactory()
        user.is_staff = True
        user.save()
        self.user = user
        self.assertTrue(self.client.login(username=user.username, password='password'))

        site = Site.objects.first()
        siteperms = SitePermission.objects.create(user=user)
        siteperms.sites.add(site)

    def test_render_add_resource(self):
        permission = Permission.objects.get(codename='add_resource')
        self.user.user_permissions.add(permission)

        response = self.client.get('/admin/lessons/resource/add/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Add resource', response.content)
        self.assertIn('Download URL', response.content)
        self.assertNotIn('Force I18n', response.content, 'privileged field should not be visible')

        permission = Permission.objects.get(codename='access_all_resources')
        self.user.user_permissions.add(permission)

        response = self.client.get('/admin/lessons/resource/add/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Add resource', response.content)
        self.assertIn('Download URL', response.content)
        self.assertIn('Force I18n', response.content, 'privileged field should be visible')

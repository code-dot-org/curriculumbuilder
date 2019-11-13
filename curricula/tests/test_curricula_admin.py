from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site

from mezzanine.core.models import SitePermission

from curricula.factories import UserFactory


# Tests for admin pages in lessons/admin.py
class CurriculaAdminTestCase(TestCase):

    def setUp(self):
        user = UserFactory()
        user.is_staff = True
        user.save()
        self.user = user
        self.assertTrue(self.client.login(username=user.username, password='password'))

        site = Site.objects.first()
        siteperms = SitePermission.objects.create(user=user)
        siteperms.sites.add(site)

    def test_render_add_curriculum(self):
        permission = Permission.objects.get(codename='add_curriculum')
        self.user.user_permissions.add(permission)

        response = self.client.get('/admin/curricula/curriculum/add/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Add curriculum', response.content)
        self.assertIn('Frameworks', response.content)
        self.assertNotIn('Ancestor', response.content, 'privileged field should not be visible')
        self.assertNotIn('Show in menus', response.content, 'privileged field should not be visible')

        permission = Permission.objects.get(codename='access_all_resources')
        self.user.user_permissions.add(permission)

        response = self.client.get('/admin/curricula/curriculum/add/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Add curriculum', response.content)
        self.assertIn('Frameworks', response.content)
        self.assertIn('Ancestor', response.content, 'privileged field should be visible')
        self.assertIn('Show in menus', response.content, 'privileged field should be visible')

    def test_render_add_unit(self):
        permission = Permission.objects.get(codename='add_unit')
        self.user.user_permissions.add(permission)

        response = self.client.get('/admin/curricula/unit/add/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Add unit', response.content)
        self.assertNotIn('Forum url', response.content, 'privileged field should not be visible')
        self.assertNotIn('Show in menus', response.content, 'privileged field should not be visible')

        permission = Permission.objects.get(codename='access_all_lessons')
        self.user.user_permissions.add(permission)

        response = self.client.get('/admin/curricula/unit/add/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Add unit', response.content)
        self.assertIn('Forum url', response.content, 'privileged field should be visible')
        self.assertIn('Show in menus', response.content, 'privileged field should be visible')

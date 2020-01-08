from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site

from mezzanine.core.models import SitePermission

from curricula.factories import UserFactory

class DocumentationAdminTestCase(TestCase):
    def setUp(self):
        user = UserFactory()
        user.is_staff = True
        user.save()
        self.user = user
        self.assertTrue(self.client.login(username=user.username, password='password'))

        site = Site.objects.first()
        siteperms = SitePermission.objects.create(user=user)
        siteperms.sites.add(site)

    def render_add(self, type):
        response = self.client.get('/admin/documentation/'+type+'/add/')
        self.assertEqual(response.status_code, 403)

        permission = Permission.objects.get(codename='add_'+type)
        self.user.user_permissions.add(permission)

        response = self.client.get('/admin/documentation/'+type+'/add/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Add '+type, response.content)

    def test_render_add_ide(self):
        self.render_add('ide')

    def test_render_add_block(self):
        self.render_add('block')

    def test_render_add_map(self):
        self.render_add('map')
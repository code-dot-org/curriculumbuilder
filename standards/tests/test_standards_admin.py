from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site

from mezzanine.core.models import SitePermission

from curricula.factories import UserFactory


class StandardsAdminTestCase(TestCase):
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
        response = self.client.get('/admin/standards/%s/add/' % type)
        self.assertEqual(response.status_code, 403)

        permission = Permission.objects.get(content_type__app_label='standards', codename='add_%s' % type)
        self.user.user_permissions.add(permission)

        response = self.client.get('/admin/standards/%s/add/' % type)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Add %s' % type, response.content)

    def test_render_add_category(self):
        self.render_add('category')

    def test_render_add_standard(self):
        self.render_add('standard')

    def test_render_add_framework(self):
        self.render_add('framework')

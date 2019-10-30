from django.test import TestCase

from curricula.factories import UserFactory


# Tests for admin pages in lessons/admin.py
class LessonsAdminTestCase(TestCase):

    def setUp(self):
        user = UserFactory()
        user.is_staff = True
        user.save()
        self.user = user
        self.client.login(username=user.username, password='password')

    def test_render_add_resource(self):
        response = self.client.get('/admin/lessons/resource/add/')
        self.assertEqual(response.status_code, 200)

from django.test import TestCase
from django.contrib.auth.models import Permission

from curricula.factories import UserFactory, CurriculumFactory, UnitFactory
from lessons.factories import LessonFactory, ResourceFactory


class CurriculaRenderingTestCase(TestCase):
    def setUp(self):
        user = UserFactory()
        user.is_staff = True
        user.save()
        self.user = user
        self.client.login(username=user.username, password='password')

        self.test_curriculum = CurriculumFactory(slug="test-curriculum")
        self.csf_curriculum = CurriculumFactory(
            slug="csf-curriculum",
            unit_template_override='curricula/csf_unit.html')
        self.pl_curriculum = CurriculumFactory(
            slug="pl-curriculum",
            unit_template_override='curricula/pl_unit.html')
        self.test_unit = UnitFactory(parent=self.test_curriculum, slug="test-unit")
        self.hoc_unit = UnitFactory(
            parent=self.test_curriculum,
            slug="hoc-unit",
            lesson_template_override="curricula/hoc_lesson.html")
        self.csf_unit = UnitFactory(
            parent=self.csf_curriculum,
            slug="csf-unit",
            lesson_template_override="curricula/csf_lesson.html")
        self.pl_unit = UnitFactory(
            parent=self.pl_curriculum,
            slug="pl-unit",
            lesson_template_override="curricula/pl_lesson.html")
        resource = ResourceFactory()
        self.test_lesson = LessonFactory(parent=self.test_unit)
        self.test_lesson.resources.add(resource)
        self.hoc_lesson = LessonFactory(parent=self.hoc_unit)
        self.hoc_lesson.resources.add(resource)
        self.csf_lesson = LessonFactory(parent=self.csf_unit)
        self.csf_lesson.resources.add(resource)
        self.pl_lesson = LessonFactory(parent=self.pl_unit)
        self.pl_lesson.resources.add(resource)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_render_curriculum(self):
        response = self.client.get('/test-curriculum/')
        self.assertEqual(response.status_code, 200)

    def test_render_unit(self):
        response = self.client.get('/test-curriculum/test-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/csf-curriculum/csf-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/hoc-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/pl-curriculum/pl-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/glance/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/vocab/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/code/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/resources/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/objectives/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/unit_feedback/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/?pdf=1')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/pl-curriculum/pl-unit/?pdf=1')
        self.assertEqual(response.status_code, 200)

    def test_render_lesson(self):
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/hoc-unit/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/csf-curriculum/csf-unit/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/pl-curriculum/pl-unit/1/')
        self.assertEqual(response.status_code, 200)

    def test_render_curriculum_admin_menu(self):
        self.assert_admin_menu('/test-curriculum/', False)
        self.assert_admin_menu('/pl-curriculum/', False)

        # Supply one combination of permissions which give the user access
        # to the admin controls in this menu. Other combinations, such as
        # when a partner views a page they own, are not covered by this test.
        self.add_permission(self.user, 'change_curriculum')
        self.add_permission(self.user, 'access_all_curricula')

        # Copy button appears in admin menu for users with sufficient permissions
        self.assert_admin_menu('/test-curriculum/', True)
        self.assert_admin_menu('/pl-curriculum/', True)

    def test_render_unit_admin_menu(self):
        self.assert_admin_menu('/test-curriculum/test-unit/', False)
        self.assert_admin_menu('/pl-curriculum/pl-unit/', False)

        # Supply one combination of permissions which give the user access
        # to the admin controls in this menu. Other combinations, such as
        # when a partner views a page they own, are not covered by this test.
        self.add_permission(self.user, 'change_unit')
        self.add_permission(self.user, 'access_all_units')

        # Copy button appears in admin menu for users with sufficient permissions
        self.assert_admin_menu('/test-curriculum/test-unit/', True)
        self.assert_admin_menu('/pl-curriculum/pl-unit/', True)

    def test_render_lesson_admin_menu(self):
        self.assert_admin_menu('/test-curriculum/test-unit/1/', False)
        self.assert_admin_menu('/test-curriculum/hoc-unit/1/', False)
        self.assert_admin_menu('/pl-curriculum/pl-unit/1/', False)

        # Supply one combination of permissions which give the user access
        # to the admin controls in this menu. Other combinations, such as
        # when a partner views a page they own, are not covered by this test.
        self.add_permission(self.user, 'change_lesson')
        self.add_permission(self.user, 'access_all_lessons')

        # Copy button appears in admin menu for users with sufficient permissions
        self.assert_admin_menu('/test-curriculum/test-unit/1/', True)
        self.assert_admin_menu('/test-curriculum/hoc-unit/1/', True)
        self.assert_admin_menu('/pl-curriculum/pl-unit/1/', True)

    def assert_admin_menu(self, path, with_admin_controls):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertIn('admin_edit', response.content)
        if with_admin_controls:
            self.assertIn('deepSpaceCopy', response.content)
            self.assertIn('Get Code Studio Stage Details', response.content)
        else:
            self.assertNotIn('deepSpaceCopy', response.content)
            self.assertNotIn('Get Code Studio Stage Details', response.content)

    def add_permission(self, user, codename):
        permission = Permission.objects.get(codename=codename)
        user.user_permissions.add(permission)

    def test_render_lesson_with_levels(self):
        stage = {
            "levels": [{
                "path": "/s/dance/stage/1/puzzle/1",
                "name": "Dance_Party_11",
                "mini_rubric": True
            },{
                "path": "/s/dance/stage/1/puzzle/2",
                "name": "Dance_Party_22",
                "teacher_markdown": "teacher markdown",
                "named_level": True
            }],
            "stageName": "test stage"
        }
        self.test_lesson.stage = stage
        self.test_lesson.save()
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)

    def test_metadata_for_course(self):
        response = self.client.get('/metadata/course/test-curriculum.json')
        self.assertEqual(response.status_code, 200)

    def test_metadata_for_unit(self):
        response = self.client.get('/metadata/test-unit.json')
        self.assertEqual(response.status_code, 200)

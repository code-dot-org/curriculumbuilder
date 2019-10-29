from django.test import TestCase
from django.contrib.auth.models import User, Permission

from curricula.models import Curriculum, Unit
from lessons.models import Lesson, Resource

from curricula.factories import UserFactory, CurriculumFactory


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
        self.test_unit = Unit.objects.create(
            title="Test Unit",
            parent=self.test_curriculum,
            slug="test-unit",
            description="Test unit description",
            show_calendar=True,
            user=user)
        self.hoc_unit = Unit.objects.create(
            title="HoC Unit",
            parent=self.test_curriculum,
            slug="hoc-unit",
            description="Hoc unit description",
            lesson_template_override="curricula/hoc_lesson.html",
            user=user)
        self.csf_unit = Unit.objects.create(
            title="CSF Unit",
            parent=self.csf_curriculum,
            slug="csf-unit",
            description="CSF unit description",
            lesson_template_override="curricula/csf_lesson.html",
            user=user)
        self.pl_unit = Unit.objects.create(
            title="PL Unit",
            parent=self.pl_curriculum,
            slug="pl-unit",
            description="PL unit description",
            lesson_template_override="curricula/pl_lesson.html",
            user=user)
        resource = Resource.objects.create(
            name="Test Resource",
            slug="test-resource",
            student=True,
            user=user)
        self.test_lesson = Lesson.objects.create(
            title="Test Lesson",
            parent=self.test_unit,
            overview="Overview",
            prep="Prep",
            user=user)
        self.test_lesson.resources.add(resource)
        self.hoc_lesson = Lesson.objects.create(
            title="HoC Lesson",
            parent=self.hoc_unit,
            overview="HoC Overview",
            prep="Prep",
            user=user)
        self.hoc_lesson.resources.add(resource)
        self.csf_lesson = Lesson.objects.create(
            title="CSF Lesson",
            parent=self.csf_unit,
            overview="CSF Overview",
            prep="Prep",
            user=user)
        self.csf_lesson.resources.add(resource)
        self.pl_lesson = Lesson.objects.create(
            title="PL Lesson",
            parent=self.pl_unit,
            overview="PL Overview",
            prep="Prep",
            user=user)
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

    def test_lesson_admin_menu(self):
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)
        # print(response.content)
        self.assertIn('admin_edit', response.content)
        self.assertNotIn('deepSpaceCopy', response.content)
        response = self.client.get('/test-curriculum/hoc-unit/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('admin_edit', response.content)
        self.assertNotIn('deepSpaceCopy', response.content)

        permission = Permission.objects.get(codename='change_lesson')
        self.user.user_permissions.add(permission)
        permission = Permission.objects.get(codename='access_all_lessons')
        self.user.user_permissions.add(permission)
        self.user.save()

        # Copy button appears in admin menu for users with sufficient permissions
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('admin_edit', response.content)
        self.assertIn('deepSpaceCopy', response.content)
        response = self.client.get('/test-curriculum/hoc-unit/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('admin_edit', response.content)
        self.assertIn('deepSpaceCopy', response.content)

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

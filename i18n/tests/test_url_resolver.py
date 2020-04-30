from django.test import TestCase
from django.contrib.auth.models import Permission
from django.utils import translation

from curricula.factories import UserFactory, CurriculumFactory, UnitFactory
from lessons.factories import LessonFactory, ResourceFactory, ActivityFactory
from django.conf import settings

class I18nUrlResolverTestCase(TestCase):
    def setUp(self):
        self.csf_curriculum = CurriculumFactory(
            slug="csf-curriculum",
            unit_template_override='curricula/csf_unit.html')
        self.pl_curriculum = CurriculumFactory(
            slug="pl-curriculum",
            unit_template_override='curricula/pl_unit.html')
        self.csf_unit = UnitFactory(
            parent=self.csf_curriculum,
            slug="csf-unit",
            lesson_template_override="curricula/csf_lesson.html")
        self.pl_unit = UnitFactory(
            parent=self.pl_curriculum,
            slug="pl-unit",
            lesson_template_override="curricula/pl_lesson.html")

    def test_render_curriculum(self):
        response = self.client.get('/csf-curriculum/')
        self.assertEqual(response.status_code, 200)
        for language_code, _ in settings.LANGUAGES:
            response = self.client.get('/%s/csf-curriculum/' % language_code)
            self.assertEqual(response.status_code, 200, "failed for language %s" % language_code)
            self.assertEqual(language_code, translation.get_language())

    def test_pl_lesson(self):
        response = self.client.get('/pl-curriculum/pl-unit/')
        self.assertEqual(response.status_code, 200)

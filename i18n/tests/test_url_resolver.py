from django.test import TestCase
from django.contrib.auth.models import Permission
from django.utils import translation

from curricula.factories import UserFactory, CurriculumFactory, UnitFactory
from lessons.factories import LessonFactory, ResourceFactory, ActivityFactory
from django.conf import settings
from mock import patch, Mock


@patch('i18n.utils.I18nFileWrapper.get_translated_field', Mock())
class I18nUrlResolverTestCase(TestCase):
    def setUp(self):
        self.csf_curriculum = CurriculumFactory(
            slug="csf-curriculum",
            unit_template_override='curricula/csf_unit.html')

        # URLs that start with a language prefix (in this case Polish)
        # don't work by default in Django. Check that they do in our system.
        self.pl_curriculum = CurriculumFactory(
            slug="pl-curriculum",
            unit_template_override='curricula/pl_unit.html')
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
        # Unfortunately, other tests assume that the language activated will be English
        # so let's clean up after ourselves.
        translation.activate(settings.LANGUAGE_CODE)

    def test_pl_lesson(self):
        response = self.client.get('/pl-curriculum/pl-unit/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(settings.LANGUAGE_CODE, translation.get_language())

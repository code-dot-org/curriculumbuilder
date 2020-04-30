from django.test import TestCase, override_settings
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.utils import translation

from curricula.factories import UserFactory, CurriculumFactory, UnitFactory
from lessons.factories import LessonFactory, ResourceFactory, ActivityFactory
from django.conf import settings
from i18n.utils import I18nFileWrapper
from mock import patch, Mock

@patch('i18n.utils.I18nFileWrapper.get_translated_field', Mock())
class I18nUrlResolverTestCase(TestCase):
    def setUp(self):
        self.csf_curriculum = CurriculumFactory(
            slug="csf-1718",
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
            response = self.client.get('/csf-1718/')
            self.assertEqual(response.status_code, 200)
            for language_code, _ in settings.LANGUAGES:
                cache.set("translations/%s/LC_MESSAGES/Curriculum.json" % translation.to_locale(language_code), {
            "1": {
                "description": u"Translated Description",
                "title": u"Translated Title"
            }
        })

                response = self.client.get('/%s/csf-1718/' % language_code)
                self.assertEqual(response.status_code, 200, "failed for language %s" % language_code)
                self.assertEqual(language_code, translation.get_language())

    def test_pl_lesson(self):
        response = self.client.get('/pl-curriculum/pl-unit/')
        self.assertEqual(response.status_code, 200)

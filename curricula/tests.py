from django.test import TestCase

from mezzanine.core.templatetags.mezzanine_tags import richtext_filters

from curricula.models import Curriculum, Unit
from lessons.models import Lesson
from standards.models import Category, GradeBand, Framework

class IframeDomainRestrictionTestCase(TestCase):
    """
    Test the RICHTEXT_ALLOWED_ATTRIBUTES logic that will only allow iframes to
    render certain domains
    """

    def test_allow_google_doc_iframes(self):
        richtext = '<iframe src="http://docs.google.com"></iframe>'
        self.assertEqual(richtext, richtext_filters(richtext))

    def test_reject_other_iframes(self):
        # Will reject non-google domains
        self.assertEqual('<iframe></iframe>',
                         richtext_filters('<iframe src="http://example.com"></iframe>'))

        # Will reject incomplete urls
        self.assertEqual('<iframe></iframe>',
                         richtext_filters('<iframe src="docs.google.com"></iframe>'))

class CurriculaRenderingTestCase(TestCase):
    def setUp(self):
        self.test_curriculum = Curriculum.objects.create(title="Test Curriculum", slug="test-curriculum")
        self.test_unit = Unit.objects.create(
            title="Test Unit",
            parent=self.test_curriculum,
            slug="test-unit",
            description="Test unit description",
            show_calendar=True
        )
        self.hoc_unit = Unit.objects.create(
            title="HoC Unit",
            parent=self.test_curriculum,
            slug="hoc-unit",
            description="Hoc unit description",
            lesson_template_override="curricula/hoc_lesson.html"
        )
        self.csf_unit = Unit.objects.create(
            title="CSF Unit",
            parent=self.test_curriculum,
            slug="csf-unit",
            description="CSF unit description",
            lesson_template_override="curricula/csf_lesson.html"
        )
        self.pl_unit = Unit.objects.create(
            title="PL Unit",
            parent=self.test_curriculum,
            slug="pl-unit",
            description="PL unit description",
            lesson_template_override="curricula/pl_lesson.html"
        )
        self.test_lesson = Lesson.objects.create(title="Test Lesson", parent=self.test_unit)
        self.hoc_lesson = Lesson.objects.create(title="HoC Lesson", parent=self.hoc_unit)
        self.csf_lesson = Lesson.objects.create(title="CSF Lesson", parent=self.csf_unit)
        self.pl_lesson = Lesson.objects.create(title="PL Lesson", parent=self.pl_unit)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_render_curriculum(self):
        response = self.client.get('/test-curriculum/')
        self.assertEqual(response.status_code, 200)

    def test_render_unit(self):
        response = self.client.get('/test-curriculum/test-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/csf-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/hoc-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/pl-unit/')
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

    def test_render_lesson(self):
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/hoc-unit/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/csf-unit/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/pl-unit/1/')
        self.assertEqual(response.status_code, 200)

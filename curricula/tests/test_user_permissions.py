from django.test import TestCase

from lessons.factories import LessonFactory
from curricula.factories import CurriculumFactory, UnitFactory, ChapterFactory, UserFactory, GroupFactory

# Tests for admin pages in lessons/admin.py
class UserPermissionsTestCase(TestCase):

    def setUp(self):
        # Create user groups with permissions
        author_group = GroupFactory.create(type='author')
        partner_group = GroupFactory.create(type='partner')

        # Set up users
        partner_user = UserFactory.create(is_staff=True, group=partner_group)
        self.partner_user = partner_user
        author_user = UserFactory.create(is_staff=True, group=author_group)
        self.author_user = author_user

        # Create curriculum, unit, chapter, lesson
        self.partner_curriculum = CurriculumFactory(user=partner_user)
        self.partner_unit = UnitFactory(user=partner_user, parent=self.partner_curriculum)
        self.partner_chapter = ChapterFactory(user=partner_user, parent=self.partner_unit)
        self.partner_lesson = LessonFactory(user=partner_user, parent=self.partner_unit)

        self.author_curriculum = CurriculumFactory(user=author_user)
        self.author_unit = UnitFactory(user=author_user, parent=self.author_curriculum)
        self.author_chapter = ChapterFactory(user=author_user, parent=self.author_unit)
        self.author_lesson = LessonFactory(user=author_user, parent=self.author_unit)

    def assert_editable_by(self, object, user, editable):
        request = self.client.get('')
        request.user = user
        self.assertEqual(object.is_editable(request), editable)

    # is_editable
    def test_partner_curriculum_is_editable_by_partner(self):
        self.assert_editable_by(self.partner_curriculum, self.partner_user, True)

    def test_partner_curriculum_is_editable_by_author(self):
        self.assert_editable_by(self.partner_curriculum, self.author_user, True)

    def test_author_curriculum_is_not_editable_by_partner(self):
        self.assert_editable_by(self.author_curriculum, self.partner_user, False)

    def test_author_curriculum_is_editable_by_author(self):
        self.assert_editable_by(self.author_curriculum, self.author_user, True)

    def test_partner_unit_is_editable_by_partner(self):
        self.assert_editable_by(self.partner_unit, self.partner_user, True)

    def test_partner_unit_is_editable_by_author(self):
        self.assert_editable_by(self.partner_unit, self.author_user, True)

    def test_author_unit_is_not_editable_by_partner(self):
        self.assert_editable_by(self.author_unit, self.partner_user, False)

    def test_author_unit_is_editable_by_author(self):
        self.assert_editable_by(self.author_unit, self.author_user, True)

    def test_partner_lesson_is_editable_by_partner(self):
        self.assert_editable_by(self.partner_lesson, self.partner_user, True)

    def test_partner_lesson_is_editable_by_author(self):
        self.assert_editable_by(self.partner_lesson, self.author_user, True)

    def test_author_lesson_is_not_editable_by_partner(self):
        self.assert_editable_by(self.author_lesson, self.partner_user, False)

    def test_author_lesson_is_editable_by_author(self):
        self.assert_editable_by(self.author_lesson, self.author_user, True)

    def test_partner_chapter_is_editable_by_partner(self):
        self.assert_editable_by(self.partner_chapter, self.partner_user, True)

    def test_partner_chapter_is_editable_by_author(self):
        self.assert_editable_by(self.partner_chapter, self.author_user, True)

    def test_author_chapter_is_not_editable_by_partner(self):
        self.assert_editable_by(self.author_chapter, self.partner_user, False)

    def test_author_chapter_is_editable_by_author(self):
        self.assert_editable_by(self.author_chapter, self.author_user, True)


    def assert_accessible_by(self, object, user, editable):
        request = self.client.get('')
        request.user = user
        self.assertEqual(object.can_access(request), editable)

    # can_access
    def test_partner_curriculum_is_accessible_by_partner(self):
        self.assert_accessible_by(self.partner_curriculum, self.partner_user, True)

    def test_partner_curriculum_is_accessible_by_author(self):
        self.assert_accessible_by(self.partner_curriculum, self.author_user, True)

    def test_author_curriculum_is_not_accessible_by_partner(self):
        self.assert_accessible_by(self.author_curriculum, self.partner_user, False)

    def test_author_curriculum_is_accessible_by_author(self):
        self.assert_accessible_by(self.author_curriculum, self.author_user, True)

    def test_partner_unit_is_accessible_by_partner(self):
        self.assert_accessible_by(self.partner_unit, self.partner_user, True)

    def test_partner_unit_is_accessible_by_author(self):
        self.assert_accessible_by(self.partner_unit, self.author_user, True)

    def test_author_unit_is_not_accessible_by_partner(self):
        self.assert_accessible_by(self.author_unit, self.partner_user, False)

    def test_author_unit_is_accessible_by_author(self):
        self.assert_accessible_by(self.author_unit, self.author_user, True)

    def test_partner_lesson_is_accessible_by_partner(self):
        self.assert_accessible_by(self.partner_lesson, self.partner_user, True)

    def test_partner_lesson_is_accessible_by_author(self):
        self.assert_accessible_by(self.partner_lesson, self.author_user, True)

    def test_author_lesson_is_not_accessible_by_partner(self):
        self.assert_accessible_by(self.author_lesson, self.partner_user, False)

    def test_author_lesson_is_accessible_by_author(self):
        self.assert_accessible_by(self.author_lesson, self.author_user, True)

    def test_partner_chapter_is_accessible_by_partner(self):
        self.assert_accessible_by(self.partner_chapter, self.partner_user, True)

    def test_partner_chapter_is_accessible_by_author(self):
        self.assert_accessible_by(self.partner_chapter, self.author_user, True)

    def test_author_chapter_is_not_accessible_by_partner(self):
        self.assert_accessible_by(self.author_chapter, self.partner_user, False)

    def test_author_chapter_is_accessible_by_author(self):
        self.assert_accessible_by(self.author_chapter, self.author_user, True)



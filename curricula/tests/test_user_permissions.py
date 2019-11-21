from django.test import TestCase

from django.contrib.auth.models import Permission

from lessons.factories import LessonFactory
from curricula.factories import CurriculumFactory, UnitFactory, ChapterFactory, UserFactory, GroupFactory

# Tests for admin pages in lessons/admin.py
class UserPermissionsTestCase(TestCase):

    def setUp(self):
        # Create user groups with permissions
        author_group = self.create_author_group()

        partner_group = self.create_partner_group()

        # Set up users
        partner_user = UserFactory()
        partner_user.is_staff = True
        partner_group.user_set.add(partner_user)
        partner_user.save()
        self.partner_user = partner_user

        author_user = UserFactory()
        author_user.is_staff = True
        author_group.user_set.add(author_user)
        author_user.save()
        self.author_user = author_user

        # Create curriculum, unit, chapter, lesson
        self.partner_curriculum = CurriculumFactory(user=partner_user, slug="partner-curriculum")
        self.partner_unit = UnitFactory(user=partner_user, parent=self.partner_curriculum, slug="partner-unit")
        self.partner_chapter = ChapterFactory(user=partner_user, parent=self.partner_unit)
        self.partner_lesson = LessonFactory(user=partner_user, parent=self.partner_unit)

        self.author_curriculum = CurriculumFactory(user=author_user, slug="author-curriculum")
        self.author_unit = UnitFactory(user=author_user, parent=self.author_curriculum, slug="author-unit")
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

    def create_author_group(self):
        author_group = GroupFactory(name="author")
        author_admin_permissions = Permission.objects.filter(content_type__app_label='admin', codename__in=[
            'add_log_entry',
        ])
        author_curricula_permissions = Permission.objects.filter(content_type__app_label='curricula', codename__in=[
            'access_all_chapters',
            'add_chapter',
            'change_chapter',
            'delete_chapter',
            'access_all_curricula',
            'add_curriculum',
            'change_curriculum',
            'delete_curriculum',
            'add_topic',
            'change_topic',
            'delete_topic',
            'access_all_units',
            'add_unit',
            'change_unit',
            'delete_unit',
        ])
        author_documentation_permissions = Permission.objects.filter(content_type__app_label='documentation',
                                                                     codename__in=[
                                                                         'add_block',
                                                                         'change_block',
                                                                         'delete_block',
                                                                         'add_category',
                                                                         'change_category',
                                                                         'delete_category',
                                                                         'add_example',
                                                                         'change_example',
                                                                         'delete_example',
                                                                         'add_ide',
                                                                         'change_ide',
                                                                         'add_map',
                                                                         'change_map',
                                                                         'delete_map',
                                                                         'add_parameter',
                                                                         'change_parameter',
                                                                         'delete_parameter',
                                                                     ])

        author_generic_permissions = Permission.objects.filter(content_type__app_label='generic',
                                                               codename__in=[
                                                                   'add_assigned_keyword',
                                                                   'change_assigned_keyword',
                                                                   'delete_assigned_keyword',
                                                                   'add_Keyword',
                                                                   'change_Keyword',
                                                                   'delete_Keyword',
                                                               ])
        author_lessons_permissions = Permission.objects.filter(content_type__app_label='lessons', codename__in=[
            'access_all_activities',
            'add_activity',
            'change_activity',
            'delete_activity',
            'add_annotation',
            'change_annotation',
            'delete_annotation',
            'access_all_lessons',
            'add_lesson',
            'add_multi_lesson',
            'change_lesson',
            'change_multi_lesson',
            'delete_lesson',
            'delete_multi_lesson',
            'access_all_objectives',
            'add_objective',
            'change_objective',
            'delete_objective',
            'add_prereq',
            'change_prereq',
            'delete_prereq',
            'access_all_resources',
            'add_resource',
            'change_resource',
            'delete_resource',
            'access_all_vocab',
            'add_vocab',
            'change_vocab',
            'delete_vocab',
        ])
        author_pages_permissions = Permission.objects.filter(content_type__app_label='pages', codename__in=[
            'add_Link',
            'change_Link',
            'delete_Link',
            'add_Page',
            'change_Page',
            'delete_Page',
            'add_Rich_text_page',
            'change_Rich_text_page',
            'delete_Rich_text_page',
        ])
        author_standards_permissions = Permission.objects.filter(content_type__app_label='standards', codename__in=[
            'change_category',
            'change_framework',
            'change_grade',
            'change_grade_band',
            'change_standard'
        ])

        author_group.permissions.add(*list(author_admin_permissions))
        author_group.permissions.add(*list(author_curricula_permissions))
        author_group.permissions.add(*list(author_documentation_permissions))
        author_group.permissions.add(*list(author_generic_permissions))
        author_group.permissions.add(*list(author_lessons_permissions))
        author_group.permissions.add(*list(author_pages_permissions))
        author_group.permissions.add(*list(author_standards_permissions))
        author_group.save()

        return author_group

    def create_partner_group(self):
        partner_group = GroupFactory(name="partner")
        partner_curricula_permissions = Permission.objects.filter(content_type__app_label='curricula', codename__in=[
            'add_chapter',
            'change_chapter',
            'change_curriculum',
            'add_unit',
            'change_unit',
        ])
        partner_lessons_permissions = Permission.objects.filter(content_type__app_label='lessons', codename__in=[
            'add_activity',
            'change_activity',
            'delete_activity',
            'add_lesson',
            'change_lesson',
            'add_objective',
            'change_objective',
            'delete_objective',
            'add_resource',
            'change_resource',
            'delete_resource',
            'add_vocab',
            'change_vocab',
            'delete_vocab',
        ])
        partner_pages_permissions = Permission.objects.filter(content_type__app_label='pages', codename__in=[
            'add_Page',
            'change_Page',
            'delete_Page'
        ])
        partner_group.permissions.add(*list(partner_curricula_permissions))
        partner_group.permissions.add(*list(partner_lessons_permissions))
        partner_group.permissions.add(*list(partner_pages_permissions))
        partner_group.save()

        return partner_group

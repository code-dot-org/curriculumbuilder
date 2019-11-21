from django.contrib.auth.models import User, Group

from factory import Sequence, PostGenerationMethodCall, SubFactory, post_generation
from factory.django import DjangoModelFactory

from django.contrib.auth.models import Permission

from curricula.models import Curriculum, Unit, Chapter


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    name = Sequence(lambda n: "group_%d" % n)

    @post_generation
    def type(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            if extracted == 'partner':
                partner_curricula_permissions = Permission.objects.filter(
                    content_type__app_label='curricula',
                    codename__in=[
                        'add_chapter',
                        'change_chapter',
                        'change_curriculum',
                        'add_unit',
                        'change_unit',
                    ]
                )
                partner_lessons_permissions = Permission.objects.filter(
                    content_type__app_label='lessons',
                    codename__in=[
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
                    ]
                )
                partner_pages_permissions = Permission.objects.filter(
                    content_type__app_label='pages',
                    codename__in=[
                        'add_Page',
                        'change_Page',
                        'delete_Page'
                    ]
                )
                self.permissions.add(*list(partner_curricula_permissions))
                self.permissions.add(*list(partner_lessons_permissions))
                self.permissions.add(*list(partner_pages_permissions))
                self.save()
            elif extracted == 'author':
                author_admin_permissions = Permission.objects.filter(
                    content_type__app_label='admin',
                    codename__in=[
                        'add_log_entry',
                    ]
                )
                author_curricula_permissions = Permission.objects.filter(
                    content_type__app_label='curricula',
                    codename__in=[
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
                    ]
                )
                author_documentation_permissions = Permission.objects.filter(
                    content_type__app_label='documentation',
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
                        'change_map',
                        'delete_map',
                        'add_parameter',
                        'change_parameter',
                        'delete_parameter',
                    ]
                )

                author_generic_permissions = Permission.objects.filter(
                    content_type__app_label='generic',
                    codename__in=[
                        'add_assigned_keyword',
                        'change_assigned_keyword',
                        'delete_assigned_keyword',
                        'add_Keyword',
                        'change_Keyword',
                        'delete_Keyword',
                    ]
                )
                author_lessons_permissions = Permission.objects.filter(
                    content_type__app_label='lessons',
                    codename__in=[
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
                    ]
                )
                author_pages_permissions = Permission.objects.filter(
                    content_type__app_label='pages',
                    codename__in=[
                        'add_Link',
                        'change_Link',
                        'delete_Link',
                        'add_Page',
                        'change_Page',
                        'delete_Page',
                        'add_Rich_text_page',
                        'change_Rich_text_page',
                        'delete_Rich_text_page',
                    ]
                )
                author_standards_permissions = Permission.objects.filter(
                    content_type__app_label='standards',
                    codename__in=[
                        'change_category',
                        'change_framework',
                        'change_grade',
                        'change_grade_band',
                        'change_standard'
                    ]
                )

                self.permissions.add(*list(author_admin_permissions))
                self.permissions.add(*list(author_curricula_permissions))
                self.permissions.add(*list(author_documentation_permissions))
                self.permissions.add(*list(author_generic_permissions))
                self.permissions.add(*list(author_lessons_permissions))
                self.permissions.add(*list(author_pages_permissions))
                self.permissions.add(*list(author_standards_permissions))
                self.save()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: "user_%d" % n)
    password = PostGenerationMethodCall('set_password', 'password')

    @post_generation
    def is_staff(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            self.is_staff = extracted

    @post_generation
    def group(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            self.groups.add(extracted)

class CurriculumFactory(DjangoModelFactory):
    class Meta:
        model = Curriculum

    title = Sequence(lambda n: "Test Curriculum %03d" % n)
    slug = Sequence(lambda n: "test-curriculum-%03d" % n)
    assessment_commentary = "Assessment Commentary"
    user = SubFactory('curricula.factories.UserFactory')

class UnitFactory(DjangoModelFactory):
    class Meta:
        model = Unit

    title = Sequence(lambda n: "Test Unit %03d" % n)
    slug = Sequence(lambda n: "test-unit-%03d" % n)
    description = "unit description"
    user = SubFactory('curricula.factories.UserFactory')

class ChapterFactory(DjangoModelFactory):
    class Meta:
        model = Chapter

    title = Sequence(lambda n: "Test Chapter %03d" % n)
    description = "chapter description"
    user = SubFactory('curricula.factories.UserFactory')

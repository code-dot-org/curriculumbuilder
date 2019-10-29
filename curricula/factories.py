from django.contrib.auth.models import User

from factory import Sequence, PostGenerationMethodCall, SubFactory
from factory.django import DjangoModelFactory

from curricula.models import Curriculum, Unit


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: "user_%d" % n)
    password = PostGenerationMethodCall('set_password', 'password')

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
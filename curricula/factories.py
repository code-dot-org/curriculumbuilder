from factory import Sequence
from factory.django import DjangoModelFactory

from curricula.models import Curriculum

class CurriculumFactory(DjangoModelFactory):
    class Meta:
        model = Curriculum

    title = Sequence(lambda n: "Test Curriculum %03d" % n)
    slug = Sequence(lambda n: "test-curriculum-%03d" % n)
    assessment_commentary = "Assessment Commentary"

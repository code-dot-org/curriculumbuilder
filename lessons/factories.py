from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from lessons.models import Lesson

class LessonFactory(DjangoModelFactory):
    class Meta:
        model = Lesson

    title = Sequence(lambda n: "Test Lesson %03d" % n)
    slug = Sequence(lambda n: "test-lesson-%03d" % n)
    overview = 'overview'
    prep = 'prep'
    user = SubFactory('curricula.factories.UserFactory')
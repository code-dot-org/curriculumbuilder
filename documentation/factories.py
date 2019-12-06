from factory import Sequence
from factory.django import DjangoModelFactory

from documentation.models import Map

class MapFactory(DjangoModelFactory):
    class Meta:
        model = Map

    title = Sequence(lambda n: "Concept %03d" % n)
    slug = Sequence(lambda n: "/concepts/%03d" % n)
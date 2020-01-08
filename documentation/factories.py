from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from documentation.models import Map, Block, IDE, Category

class MapFactory(DjangoModelFactory):
    class Meta:
        model = Map

    title = Sequence(lambda n: "Concept %03d" % n)
    slug = Sequence(lambda n: "/concepts/%03d" % n)

class BlockFactory(DjangoModelFactory):
    class Meta:
        model = Block

    title = Sequence(lambda n: "Block %03d" % n)
    slug = Sequence(lambda n: "%03d" % n)
    parent_ide = SubFactory('documentation.factories.IDEFactory')
    parent = parent_ide

class IDEFactory(DjangoModelFactory):
    class Meta:
        model = IDE

    title = Sequence(lambda n: "IDE %03d" % n)
    slug = Sequence(lambda n: "%03d" % n)

class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = Sequence(lambda n: "Category %03d" % n)
    parent_ide = SubFactory('documentation.factories.IDEFactory')

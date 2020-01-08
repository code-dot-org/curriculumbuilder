from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from standards.models import Standard, GradeBand, Category, Framework

class StandardFactory(DjangoModelFactory):
    class Meta:
        model = Standard

    name = Sequence(lambda n: "Standard %03d" % n)
    gradeband = SubFactory('standards.factories.GradeBandFactory')
    category = SubFactory('standards.factories.CategoryFactory')
    framework = SubFactory('standards.factories.FrameworkFactory')

class GradeBandFactory(DjangoModelFactory):
    class Meta:
        model = GradeBand

    name = Sequence(lambda n: "GradeBand %03d" % n)

class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = Sequence(lambda n: "Category %03d" % n)
    framework = SubFactory('standards.factories.FrameworkFactory')
    # Need to set parent to none on subfactory so that we don't end up with infinite recursion
    parent = SubFactory('standards.factories.CategoryFactory', parent=None)

class FrameworkFactory(DjangoModelFactory):
    class Meta:
        model = Framework

    name = Sequence(lambda n: "Framework %03d" % n)

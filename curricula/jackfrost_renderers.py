from django.core.urlresolvers import reverse
from jackfrost.models import ModelRenderer

from curricula.models import *
from lessons.models import *
from documentation.models import *


def homeRenderer():
    return [reverse('curriculum:home')]


class CurriculumRenderer(ModelRenderer):
    def get_model(self):
        return Curriculum


class UnitRenderer(ModelRenderer):
    def get_model(self):
        return Unit


class UnitPDFRenderer(ModelRenderer):
    def get_model(self):
        return Unit

    def get_urls(self):
        for obj in self.get_paginated_queryset():

            if hasattr(obj, 'jackfrost_can_build'):
                if obj.jackfrost_can_build() is False:
                    continue

            if hasattr(obj, 'pdf_urls'):
                for url in obj.pdf_urls():
                    yield url


class LessonRenderer(ModelRenderer):
    def get_model(self):
        return Lesson


class IDERenderer(ModelRenderer):
    def get_model(self):
        return IDE


class BlockRenderer(ModelRenderer):
    def get_model(self):
        return Block


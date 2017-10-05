from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField
from django.db.models import Q
from django.forms.models import model_to_dict
from collections import OrderedDict
from sortedcontainers import SortedDict
from curricula.models import Unit, Curriculum
from curricula.serializers import LessonSerializer
from lessons.models import Lesson
from standards.models import Standard, Category, Framework


class RecursiveManyRelatedField(serializers.ManyRelatedField, serializers.BaseSerializer):
    """
    Workaround to avoid "assert issubclass(parent_class, BaseSerializer)"
    """
    pass


class StandardSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        # depth = 2
        model = Standard
        fields = ('name', 'shortcode', 'lessons')

    def get_lessons(self, obj):
        curriculum = self.context['curriculum']
        # lessons = list( Lesson.objects.filter(parent__parent=curriculum).values('title',) )
        filtered_lessons = Lesson.objects.filter(parent__parent=curriculum, standards=obj)
        # filtered_lessons = Lesson.objects.all()
        serializer = LessonSerializer(filtered_lessons, many=True)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        depth = 2


class FrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Framework
        depth = 2


'''
What follows is a rewrite of the serializers to allow for a single nested request
If this works out well, I may want to trash the previous serializers

'''


class StandardListSerializer(serializers.ListSerializer):
    def to_representation(self, instance):
        standards = super(StandardListSerializer, self).to_representation(instance)

        return SortedDict({std['shortcode']: dict(std) for std in standards})


class NestedStandardSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Standard
        fields = ('name', 'shortcode', 'lessons', 'lesson_count')
        list_serializer_class = StandardListSerializer

    def get_lessons(self, obj):
        curriculum = self.context['curriculum']
        filtered_lessons = Lesson.objects.filter(parent__parent=curriculum, standards=obj)
        serializer = LessonSerializer(filtered_lessons, many=True)
        return serializer.data

    # If lesson_count turns out to be useful, should probably integrated into model
    def get_lesson_count(self, obj):
        curriculum = self.context['curriculum']
        count = Lesson.objects.filter(parent__parent=curriculum, standards=obj).count()
        return count


class NestedSubCategorySerializer(serializers.ModelSerializer):
    standard_set = NestedStandardSerializer(many=True, read_only=True)
    children = RecursiveManyRelatedField(child_relation=RecursiveField(to='NestedCategorySerializer', allow_null=True),
                                         read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('shortcode', 'name', 'type', 'children', 'standard_set', 'lesson_count')
        list_serializer_class = StandardListSerializer

    def get_lesson_count(self, obj):
        curriculum = self.context['curriculum']
        # To avoid counting the same lesson multiple times because it belongs to multiple child categories
        # We flatten the list to pks only and then filter for distinct pks before counting
        count = Lesson.objects.filter(Q(standards__category=obj) | Q(standards__category__parent=obj),
                                      parent__parent=curriculum).distinct().count()
        return count


class NestedCategorySerializer(serializers.ModelSerializer):
    standard_set = NestedStandardSerializer(many=True, read_only=True)
    children = NestedSubCategorySerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('shortcode', 'name', 'type', 'children', 'standard_set', 'lesson_count')
        # list_serializer_class = CategoryListSerializer

    def get_lesson_count(self, obj):
        curriculum = self.context['curriculum']
        # To avoid counting the same lesson multiple times because it belongs to multiple child categories
        # We flatten the list to pks only and then filter for distinct pks before counting
        count = Lesson.objects.filter(Q(standards__category=obj) | Q(standards__category__parent=obj),
                                      parent__parent=curriculum).distinct().count()
        return count


class NestedFrameworkSerializer(serializers.ModelSerializer):
    children = NestedCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Framework
        # fields =


class FrameworkHeatmap(serializers.ModelSerializer):
    class Meta:
        model = Framework
        fields = ('slug', 'name',)


'''
json_response = []
for standard in Standard.objects.filter(framework__slug=framework_slug):
  for lesson in standard.lesson_set.filter(parent__parent__slug=curriculum_slug):
    json_response.append([standard.shortcode, standard.name, standard.category.shortcode, standard.category.name, standard.category.parent.shortcode, standard.category.parent.name, lesson.number(), lesson.title])

json.dumps(json_response)
'''

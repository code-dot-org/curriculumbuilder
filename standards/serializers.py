from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField
from collections import OrderedDict
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
    #depth = 2
    model = Standard
    fields = ('name', 'shortcode', 'lessons')


  def get_lessons(self, obj):
    curriculum = self.context['curriculum']
    #lessons = list( Lesson.objects.filter(parent__parent=curriculum).values('title',) )
    filtered_lessons = Lesson.objects.filter(parent__parent=curriculum, standards=obj)
    #filtered_lessons = Lesson.objects.all()
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

class NestedStandardSerializer(serializers.ModelSerializer):

  lessons = serializers.SerializerMethodField()
  lesson_count = serializers.SerializerMethodField()

  class Meta:
    model = Standard
    fields = ('name', 'shortcode', 'lessons', 'lesson_count')

  def get_lessons(self, obj):
    curriculum = self.context['curriculum']
    filtered_lessons = Lesson.objects.filter(parent__parent=curriculum, standards=obj)
    serializer = LessonSerializer(filtered_lessons, many=True)
    return serializer.data

  def get_lesson_count(self, obj):
    curriculum = self.context['curriculum']
    count = Lesson.objects.filter(parent__parent=curriculum, standards=obj).count()
    return count

class NestedCategorySerializer(serializers.ModelSerializer):

  standard_set = NestedStandardSerializer(many=True, read_only=True)
  children = RecursiveManyRelatedField(child_relation=RecursiveField(to='NestedCategorySerializer', allow_null=True), read_only=True)
  lesson_count = serializers.SerializerMethodField()

  class Meta:
    model = Category
    fields = ('name', 'shortcode', 'type', 'children', 'standard_set', 'lesson_count')

  def get_lesson_count(self, obj):
    curriculum = self.context['curriculum']
    # To avoid counting the same lesson multiple times because it belongs to multiple child categories
    # We flatten the list to pks only and then filter for distinct pks before counting
    count = Lesson.objects.filter(parent__parent=curriculum, standards__category=obj).values_list('pk',flat=True).distinct().count()
    return count

class NestedFrameworkSerializer(serializers.ModelSerializer):

  children = NestedCategorySerializer(many=True, read_only=True)

  class Meta:
    model = Framework
    #fields =


'''
json_response = []
for standard in Standard.objects.filter(framework__slug=framework_slug):
  for lesson in standard.lesson_set.filter(parent__parent__slug=curriculum_slug):
    json_response.append([standard.shortcode, standard.name, standard.category.shortcode, standard.category.name, standard.category.parent.shortcode, standard.category.parent.name, lesson.number(), lesson.title])

json.dumps(json_response)
'''
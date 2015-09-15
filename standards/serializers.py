from rest_framework import serializers
from curricula.models import Unit, Curriculum
from curricula.serializers import LessonSerializer
from lessons.models import Lesson
from standards.models import Standard, Category, Framework

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


'''
json_response = []
for standard in Standard.objects.filter(framework__slug=framework_slug):
  for lesson in standard.lesson_set.filter(parent__parent__slug=curriculum_slug):
    json_response.append([standard.shortcode, standard.name, standard.category.shortcode, standard.category.name, standard.category.parent.shortcode, standard.category.parent.name, lesson.number(), lesson.title])

json.dumps(json_response)
'''
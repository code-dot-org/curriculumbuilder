from rest_framework import serializers
from curricula.models import Unit, Curriculum
from lessons.models import Lesson

class LessonSerializer(serializers.ModelSerializer):

  unit = serializers.SerializerMethodField()
  unit_number = serializers.SerializerMethodField()

  class Meta:
    model = Lesson
    #depth = 1
    fields = ('title', 'number', 'unit', 'unit_number', 'description')

  def get_unit(self, obj):
    return obj.unit.title

  def get_unit_number(self, obj):
    return obj.unit.number

class UnitSerializer(serializers.ModelSerializer):

  lessons = serializers.SerializerMethodField()

  class Meta:
    model = Unit
    #depth = 1
    fields = ('title', 'slug', 'description', 'number', 'curriculum', 'lessons')

  def get_lessons(self, obj):
    lessons = obj.lessons
    serializer = LessonSerializer(lessons, many=True)
    return serializer.data

class CurriculumSerializer(serializers.ModelSerializer):

  units = serializers.SerializerMethodField()

  class Meta:
    model = Curriculum
    #depth = 2
    fields = ('title', 'slug', 'description', 'units')

  def get_units(self, obj):
    units = obj.units
    serializer = UnitSerializer(units, many=True)
    return serializer.data
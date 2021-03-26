import json
from rest_framework import serializers

from curricula.models import Unit, Chapter, Curriculum
from lessons.models import Lesson, Activity, Resource, Vocab, Annotation, Standard, Block
from documentation.models import Block

"""
Curriculum serializers
"""

class ResourceSerializer(serializers.ModelSerializer):
    html = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = ('name', 'type', 'url', 'html')

    def get_html(self, obj):
        if self.context.get('with_html') and obj.gd:
            return obj.gd_html()


class VocabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocab
        fields = ('word', 'simpleDef', 'detailDef')


class BlockSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ('title', 'syntax', 'url')

    def get_url(self, obj):
        return obj.get_published_url()


class LessonSerializer(serializers.ModelSerializer):
    teacher_desc = serializers.SerializerMethodField()
    student_desc = serializers.SerializerMethodField()
    teacher_resources = serializers.SerializerMethodField()
    student_resources = serializers.SerializerMethodField()
    vocab = serializers.SerializerMethodField()
    blocks = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ('title', 'number', 'student_desc', 'teacher_desc',
                  'student_resources', 'teacher_resources', 'vocab', 'blocks')

    def get_teacher_desc(self, obj):
        return obj.overview

    def get_student_desc(self, obj):
        return obj.description

    def get_teacher_resources(self, obj):
        resources = obj.resources.filter(student=False)
        serializer = ResourceSerializer(resources, many=True, context=self.context)
        return serializer.data

    def get_student_resources(self, obj):
        resources = obj.resources.filter(student=True)
        serializer = ResourceSerializer(resources, many=True, context=self.context)
        return serializer.data

    def get_vocab(self, obj):
        vocab = obj.vocab.all()
        serializer = VocabSerializer(vocab, many=True)
        return serializer.data

    def get_blocks(self, obj):
        blocks = obj.blocks.all()
        serializer = BlockSerializer(blocks, many=True)
        return serializer.data


class UnitSerializer(serializers.ModelSerializer):
    teacher_desc = serializers.SerializerMethodField()
    student_desc = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ('title', 'number', 'slug', 'unit_name', 'student_desc', 'teacher_desc', 'lessons')

    def get_teacher_desc(self, obj):
        return obj.content

    def get_student_desc(self, obj):
        return obj.description

    def get_lessons(self, obj):
        lessons = obj.lessons
        serializer = LessonSerializer(lessons, many=True, context=self.context)
        return serializer.data


class CurriculumSerializer(serializers.ModelSerializer):
    units = serializers.SerializerMethodField()
    teacher_desc = serializers.SerializerMethodField()
    student_desc = serializers.SerializerMethodField()

    class Meta:
        model = Curriculum
        fields = ('title', 'slug', 'student_desc', 'teacher_desc', 'units')

    def get_units(self, obj):
        units = obj.units
        serializer = UnitSerializer(units, many=True, context=self.context)
        return serializer.data

    def get_teacher_desc(self, obj):
        return obj.content

    def get_student_desc(self, obj):
        return obj.description


"""
Export serializers
"""

class UnitExportSerializer(serializers.ModelSerializer):
    chapters = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()
    student_desc = serializers.SerializerMethodField()
    teacher_desc = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ('title', 'number', 'slug', 'unit_name', 'show_calendar', 'student_desc', 'teacher_desc', 'chapters', 'lessons')

    def get_teacher_desc(self, obj):
        return obj.content

    def get_student_desc(self, obj):
        return obj.description

    # A lesson could either appear directly in lessons, or nested within chapters.
    # In 2020 courses, CSF and CSD use chapters but CSP does not.

    def get_chapters(self, obj):
        chapters = obj.chapters
        serializer = ChapterExportSerializer(chapters, many=True, context=self.context)
        return serializer.data

    def get_lessons(self, obj):
        # Only include lessons which are direct children of this unit, omitting any
        # children of chapters in this unit.
        lessons = Lesson.objects.filter(parent__unit=obj)
        serializer = LessonExportSerializer(lessons, many=True, context=self.context)
        return serializer.data


class ChapterExportSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ('title', 'number', 'questions', 'description', 'lessons')

    def get_lessons(self, obj):
        lessons = obj.lessons
        serializer = LessonExportSerializer(lessons, many=True, context=self.context)
        return serializer.data


class LessonExportSerializer(serializers.ModelSerializer):
    teacher_desc = serializers.SerializerMethodField()
    student_desc = serializers.SerializerMethodField()
    activities = serializers.SerializerMethodField()
    resources = serializers.SerializerMethodField()
    vocab = serializers.SerializerMethodField()
    blocks = serializers.SerializerMethodField()
    objectives = serializers.SerializerMethodField()
    standards = serializers.SerializerMethodField()
    stage_name = serializers.SerializerMethodField()
    creative_commons_license = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ('title', 'number', 'student_desc', 'teacher_desc', 'activities', 'resources',
                  'vocab', 'blocks', 'objectives', 'standards', 'code_studio_url', 'stage_name',
                  'prep', 'cs_content', 'creative_commons_license', 'assessment')

    def get_teacher_desc(self, obj):
        return obj.overview

    def get_student_desc(self, obj):
        return obj.description

    def get_activities(self, obj):
        activities = obj.activity_set.iterator()
        serializer = ActivityExportSerializer(activities, many=True, context=self.context)
        return serializer.data

    def get_resources(self, obj):
        resources = obj.resources
        serializer = ResourceExportSerializer(resources, many=True, context=self.context)
        return serializer.data

    def get_vocab(self, obj):
        vocab = obj.vocab.all()
        serializer = VocabExportSerializer(vocab, many=True, context=self.context)
        return serializer.data

    def get_blocks(self, obj):
        blocks = obj.blocks.all()
        serializer = BlockExportSerializer(blocks, many=True, context=self.context)
        return serializer.data

    def get_objectives(self, obj):
        return obj.objective_set.values('name')

    def get_standards(self, obj):
        standards = obj.standards.all()
        serializer = StandardSerializer(standards, many=True, context=self.context)
        return serializer.data

    def get_stage_name(self, obj):
        if obj.stage:
            return obj.stage['stageName']
        return ''

    def get_creative_commons_license(self, obj):
        img_to_license = {
            'img/creativeCommons-by-nc-sa.png': 'Creative Commons BY-NC-SA',
            'img/creativeCommons-by-nc-nd.png': 'Creative Commons BY-NC-ND'
        }
        return img_to_license[obj.creative_commons_image]


class ActivityExportSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ('name', 'duration', 'content')

    def get_duration(self, obj):
        return obj.time


class ResourceExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('name', 'type', 'student', 'gd', 'url', 'dl_url', 'slug')

class VocabExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocab
        fields = ('word', 'simpleDef', 'detailDef')

class BlockExportSerializer(serializers.ModelSerializer):
    parent_slug = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ('slug', 'parent_slug')

    def get_parent_slug(self, obj):
        return obj.parent_ide.slug

"""
Standards serializers
"""


class UnitLessonsSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ('unit_name', 'lessons')

    def get_lessons(self, obj):
        lessons = obj.lessons
        serializer = LessonStandardsSerializer(lessons, many=True, context=self.context)
        return serializer.data


class LessonStandardsSerializer(serializers.ModelSerializer):
    standards = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ('title', 'number', 'standards')

    def get_standards(self, obj):
        standards = obj.standards.all()
        serializer = StandardSerializer(standards, many=True)
        return serializer.data


class StandardSerializer(serializers.ModelSerializer):
    framework = serializers.SerializerMethodField()

    class Meta:
        model = Standard
        fields = ('shortcode', 'framework')

    def get_framework(self, obj):
        return obj.framework.slug


"""
Annotation serializers
"""


class Range():
    def __init__(self, start, end, startOffset, endOffset):
        self.start = start
        self.end = end
        self.startOffset = startOffset
        self.endOffset = endOffset


class RangeSerializer(serializers.BaseSerializer):
    start = serializers.CharField(max_length=50)
    end = serializers.CharField(max_length=50)
    startOffset = serializers.IntegerField()
    endOffset = serializers.IntegerField()

    def to_representation(self, obj):
        ranges = Range(obj[0], obj[1], obj[2], obj[3])
        return [ranges.__dict__]

    def to_internal_value(self, data):
        try:
            start = data[0]['start']
            end = data[0]['end']
            startOffset = data[0]['startOffset']
            endOffset = data[0]['endOffset']
            return Range(start, end, startOffset, endOffset)
        except AttributeError:
            return AttributeError


'''
class AnnotationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Annotation
        fields = ('pk', 'owner', 'lesson', 'annotator_schema_version', 'text', 'quote', 'uri', 'range_start',
				        				'range_end', 'range_startOffset', 'range_endOffset')
'''


class AnnotationSerializer(serializers.Serializer):
    id = serializers.CharField(label="id", required=False)
    annotator_schema_version = serializers.CharField(max_length=8, allow_blank=True, required=False)
    created = serializers.CharField(allow_blank=True, required=False)
    updated = serializers.CharField(source='modified', allow_blank=True, required=False)
    text = serializers.CharField()
    quote = serializers.CharField()
    uri = serializers.CharField(max_length=100, min_length=None, allow_blank=True, required=False)
    ranges = RangeSerializer()
    user = serializers.CharField(source='owner', label='user', required=False)
    lesson = serializers.CharField()

    def update(self, instance, validated_data):
        instance.annotator_schema_version = validated_data.get('annotator_schema_version',
                                                               instance.annotator_schema_version)
        instance.text = validated_data.get('text', instance.text)
        instance.quote = validated_data.get('quote', instance.quote)
        instance.uri = validated_data.get('uri', instance.uri)

        # Unpacking the ranges dict into 4 fields in instance.
        try:
            ranges = validated_data['ranges']
            instance.range_start = ranges.start
            instance.range_end = ranges.end
            instance.range_startOffset = ranges.startOffset
            instance.range_endOffset = ranges.endOffset
        except KeyError:
            print "No ranges array passed to AnnotationSerializer."

        instance.save()
        return instance

    def create(self, validated_data):
        annotation = dict()
        annotation['owner'] = self.context['request'].user
        annotation['quote'] = validated_data.get('quote')
        annotation['text'] = validated_data.get('text')
        annotation['uri'] = validated_data.get('uri')
        annotation['lesson'] = Lesson.objects.get(pk=validated_data.get('lesson'))

        # Unpacking the ranges dict into 4 fields in instance.
        try:
            ranges = validated_data['ranges']
            annotation['range_start'] = ranges.start
            annotation['range_end'] = ranges.end
            annotation['range_startOffset'] = ranges.startOffset
            annotation['range_endOffset'] = ranges.endOffset
        except KeyError:
            print "No ranges array passed to AnnotationSerializer."

        return Annotation.objects.create(**annotation)

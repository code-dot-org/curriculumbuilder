from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import autoselect_fields_check_can_add
from django.contrib import admin
from django.db import models
from django.forms import TextInput, ModelForm
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from mezzanine.generic.fields import KeywordsField
from mezzanine.pages.admin import PageAdmin
from reversion.admin import VersionAdmin
from reversion_compare.admin import CompareVersionAdmin

from curriculumBuilder import settings
from lessons.models import Lesson, Objective, Prereq, Activity, Vocab, Resource, Annotation
from curricula.models import Curriculum, Unit
from standards.models import Standard
from documentation.models import Block


def publish(modeladmin, request, queryset):
    for obj in queryset:
        print obj


class ObjectiveInline(TabularDynamicInlineAdmin):
    model = Objective
    fields = ["name", "_order"]
    verbose_name = "Objective"
    verbose_name_plural = "Objectives"
    extra = 3

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 100, 'style': 'width: 700px'})},
    }


class ObjectiveAdmin(admin.ModelAdmin):
    model = Objective
    fields = ['name', 'lesson']
    verbose_name = "Objective"
    verbose_name_plural = "Objectives"
    list_display = ('lesson', 'name')
    list_editable = ('name',)
    list_filter = ('lesson__curriculum', 'lesson__unit')


class PrereqInline(StackedDynamicInlineAdmin):
    model = Prereq
    verbose_name = "Prerequisite"
    verbose_name_plural = "Prerequisites"
    extra = 3


class ActivityInline(StackedDynamicInlineAdmin):
    model = Activity
    verbose_name_plural = "Activities"
    extra = 5

    exclude = ['ancestor', ]


class ResourceInline(TabularDynamicInlineAdmin):
    model = Lesson.resources.through
    extra = 3

    sortable_field_name = "sort_value"
    readonly_fields = ('type', 'md_tag')
    verbose_name_plural = "Resources"

    def get_form(self, request, obj=None, **kwargs):
        form = super(ResourceInline, self).get_form(request, obj, **kwargs)
        autoselect_fields_check_can_add(form, self.model, request.user)
        return form

    def type(self, instance):
        return instance.resource.type

    def md_tag(self, instance):
        return instance.resource.md_tag()


class UnitForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row):
        return self.model.objects.filter(
            curriculum__slug=row["curriculum"],
            slug=row["unit"]
        )


'''
This import_export resource is optimized for imported standards alignments
and as such, ignores most other lesson fields
'''


class ImportLessonResource(resources.ModelResource):
    standards = fields.Field(column_name='standards', attribute='standards',
                             widget=ManyToManyWidget(Standard, field='slug'))

    curriculum = fields.Field(column_name='curriculum', attribute='curriculum',
                              widget=ForeignKeyWidget(Curriculum, 'slug'))

    unit = fields.Field(column_name='unit', attribute='unit',
                        widget=UnitForeignKeyWidget(Unit, 'slug'))

    class Meta:
        model = Lesson
        fields = ("id", "title", "curriculum", "number", "standards")

'''
This import_export resource is optimized for exporting to Amazon Inspire
'''


class LessonResource(resources.ModelResource):

    url = fields.Field()
    grades = fields.Field()
    keywords = fields.Field()
    subjects = fields.Field()
    license_type = fields.Field()
    resource_type = fields.Field()
    publisher = fields.Field()
    collection_name = fields.Field()
    collection_description = fields.Field()
    collection_order = fields.Field()
    collection2_name = fields.Field()
    collection2_description = fields.Field()
    collection2_order = fields.Field()

    class Meta:
        model = Lesson
        fields = ("title", "description", "url", "license_type", "grades", "subjects", "resource_type", "keywords",
                  "publisher", "collection_name", "collection_description", "collection_order", "collection2_name",
                  "collection2_description", "collection2_order")
        export_order = fields

    def dehydrate_url(self, lesson):
        return "https://%s%s" % (settings.AWS_S3_CUSTOM_DOMAIN, lesson.get_absolute_url())

    # ToDo: Replace with course/unit assigned gradeband
    def dehydrate_grades(self, lesson):
        if lesson.curriculum.slug.startswith('csf'):
            gradebands = {
                'coursea': 'Kindergarten',
                'courseb': '1',
                'coursec': '2',
                'coursed': '3',
                'coursee': '4',
                'coursef': '5',
                'pre-express': 'Kindergarten;1;2',
                'express': '3;4;5'
            }
            return gradebands.get(lesson.unit.slug, "Kindergarten;1;2;3;4;5")
        elif lesson.curriculum.slug.startswith('csd'):
            return '6;7;8;9'
        elif lesson.curriculum.slug.startswith('csp'):
            return '9;10;11;12'
        else:
            return 'Not Grade Specific'

    def dehydrate_keywords(self, lesson):
        keywords = lesson.keywords.values_list('keyword__title', flat=True)
        standards = lesson.standards.values_list('slug', flat=True)
        return list(keywords) + list(standards)

    def dehydrate_subjects(self, lesson):
        return "Computer Science"

    def dehydrate_license_type(self, lesson):
        return "Creative Commons Attribution-NonCommercial-ShareAlike 4.0"

    def dehydrate_resource_type(self, lesson):
        return "Instruction: Lesson Plan"

    def dehydrate_publisher(self, lesson):
        return "Code.org"

    def dehydrate_collection_name(self, lesson):
        return "Code.org %s" % lesson.curriculum.title

    def dehydrate_collection_description(self, lesson):
        return lesson.curriculum.description

    def dehydrate_collection_order(self, lesson):
        if lesson.is_optional:
            return "%d.%d.%d" % (lesson.unit.number, lesson.parent.lesson.number, lesson.number)
        else:
            return "%d.%d" % (lesson.unit.number, lesson.number)

    def dehydrate_collection2_name(self, lesson):
        return "Code.org %s: %s" % (lesson.curriculum.title, lesson.unit.title)

    def dehydrate_collection2_description(self, lesson):
        return lesson.unit.description

    def dehydrate_collection2_order(self, lesson):
        if lesson.is_optional:
            return "%d.%d" % (lesson.parent.lesson.number, lesson.number)
        else:
            return lesson.number


class LessonInline(TabularDynamicInlineAdmin):
    model = Lesson
    sortable_field_name = "number"
    fields = ['title', 'week', 'number', 'pacing_weight', 'unplugged', 'keywords']

    keywords = KeywordsField()


class LessonForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(LessonForm, self).__init__(*args, **kwargs)

        '''
        Load standards only once (for both fields) and filter down to curriculum aligned standards, if available
        '''
        standards_queryset = None

        try:
            curriculum = None
            if hasattr(self.instance.parent, 'chapter'):
                curriculum = self.instance.parent.chapter.curriculum
            elif hasattr(self.instance.parent, 'unit'):
                curriculum = self.instance.parent.unit.curriculum
            elif hasattr(self.instance.parent, 'curriculum'):
                curriculum = self.instance.parent.curriculum
            else:
                pass

            if curriculum.frameworks.count() > 0:
                standards_queryset = Standard.objects.filter(framework=curriculum.frameworks.all())
            else:
                standards_queryset = Standard.objects.all()

        except:
            standards_queryset = Standard.objects.all()

        if standards_queryset is None:
            standards_queryset = Standard.objects.all()

        self.fields['standards'].queryset = standards_queryset
        self.fields['anchor_standards'].queryset = standards_queryset

        '''
        Optimize loading of blocks with related IDEs
        '''
        self.fields['blocks'].queryset = Block.objects.all().select_related('parent_ide')


class LessonAdmin(PageAdmin, AjaxSelectAdmin, CompareVersionAdmin):
    form = LessonForm

    actions = [publish]

    inlines = [ObjectiveInline, ResourceInline, ActivityInline]

    filter_horizontal = ('standards', 'anchor_standards', 'vocab', 'blocks')

    fieldsets = (
        (None, {
            'fields': ['title', ('status', 'login_required', 'week', 'duration', 'pacing_weight', 'unplugged'), 'image',
                       'overview', 'keywords', ('description', 'gen_description')],
        }),
        ('Purpose, Prep, & Questions', {
            'fields': ['cs_content', 'prep', 'questions'],
            'classes': ['collapse-closed'],
        }),
        ('Vocab & Blocks', {
            'fields': ['vocab', 'blocks'],
            'classes': ['collapse-closed'],
        }),
        ('Standards', {
            'fields': ['standards', 'anchor_standards'],
            'classes': ['collapse-closed'],
        }),
    )

    def compare_activity(self, obj_compare):
        """ compare the foo_bar model field """
        return "%r <-> %r" % (obj_compare.value1, obj_compare.value2)

    def get_queryset(self, request):
        return super(LessonAdmin, self).get_queryset(request).select_related('parent', 'page_ptr') \
            .prefetch_related('standards', 'anchor_standards',
                              'vocab', 'resources', 'activity_set')


class MultiLessonForm(ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'week', 'number', 'pacing_weight', 'unplugged', 'keywords']

    keywords = KeywordsField()


class MultiLesson(Lesson):
    class Meta:
        proxy = True


class MultiLessonAdmin(ImportExportModelAdmin):
    resource_class = LessonResource
    list_display = ('curriculum', 'unit', 'number', 'title', 'week', 'pacing_weight', 'unplugged')
    list_editable = ('title', 'week', 'pacing_weight', 'unplugged')
    list_filter = ('curriculum', 'unit', 'keywords__keyword', 'curriculum__version')
    actions = [publish]
    form = LessonForm

    inlines = [ObjectiveInline, ResourceInline, ActivityInline]

    filter_horizontal = ('standards', 'anchor_standards', 'vocab', 'blocks')

    fieldsets = (
        (None, {
            'fields': ['title', ('status', 'login_required', 'week', 'duration', 'pacing_weight', 'unplugged'), 'image',
                       'overview', 'keywords', ('description', 'gen_description')],
        }),
        ('Purpose, Prep, & Questions', {
            'fields': ['cs_content', 'prep', 'questions'],
            'classes': ['collapse-closed'],
        }),
        ('Vocab & Blocks', {
            'fields': ['vocab', 'blocks'],
            'classes': ['collapse-closed'],
        }),
        ('Standards', {
            'fields': ['standards', 'anchor_standards'],
            'classes': ['collapse-closed'],
        }),
    )

    def get_changelist_form(self, request, **kwargs):
        return MultiLessonForm


class ResourceAdmin(AjaxSelectAdmin):
    model = Resource

    list_display = ('name', 'type', 'student', 'gd', 'url', 'dl_url')
    list_editable = ('type', 'student', 'gd', 'url', 'dl_url')


class VocabAdmin(ImportExportModelAdmin):
    model = Vocab

    list_display = ('word', 'simpleDef')
    list_editable = ('word', 'simpleDef')


class VocabResource(resources.ModelResource):
    class Meta:
        model = Vocab


class ActivityAdmin(CompareVersionAdmin):
    class Meta:
        model = Activity

    readonly_fields = ('curriculum', 'unit')
    list_display = ('curriculum', 'unit', 'lesson', 'name')
    list_filter = ('lesson__curriculum', 'lesson__unit')

    def curriculum(self, instance):
        return instance.lesson.curriculum

    def unit(self, instance):
        return instance.lesson.unit

    curriculum.admin_order_field = 'lesson__curriculum'
    unit.admin_order_field = 'lesson__unit'

class AnnotationAdmin(CompareVersionAdmin):
    pass


admin.site.register(Lesson, LessonAdmin)
admin.site.register(MultiLesson, MultiLessonAdmin)
admin.site.register(Lesson.resources.through)
admin.site.register(Prereq)
admin.site.register(Objective, ObjectiveAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Vocab, VocabAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Annotation, AnnotationAdmin)

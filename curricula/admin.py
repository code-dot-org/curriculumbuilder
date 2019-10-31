from django.contrib import admin
from django.forms import ModelForm
from mezzanine.pages.admin import PageAdmin
from mezzanine.core.admin import StackedDynamicInlineAdmin, TabularDynamicInlineAdmin
from mezzanine.generic.fields import KeywordsField
from import_export.admin import ImportExportModelAdmin

from reversion.admin import VersionAdmin

from lessons.models import Lesson
from lessons.admin import LessonForm, FilterableAdmin

from curricula.models import Curriculum, Unit, Chapter, Topic
from standards.models import Standard


class LessonInline(TabularDynamicInlineAdmin):
    model = Lesson
    fk_name = 'unit'
    fields = ['number', 'title', 'week', 'pacing_weight', 'unplugged', 'keywords']

    keywords = KeywordsField()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LessonStandardsInline(StackedDynamicInlineAdmin):
    model = Lesson
    form = LessonForm
    fk_name = 'unit'
    fields = ('standards',)
    filter_horizontal = ('standards',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class TopicInline(TabularDynamicInlineAdmin):
    model = Topic
    verbose_name_plural = "Topics"
    extra = 5


class CurriculumAdmin(PageAdmin, VersionAdmin, FilterableAdmin):
    model = Curriculum
    verbose_name_plural = "Curricula"
    filter_horizontal = ('frameworks',)
    inlines = (TopicInline,)

    def can_access_all(self, request):
        return request.user.has_perm('curricula.access_all_curricula')

    def get_fieldsets(self, request, obj=None):

        # Use the access_all permission to exclude partners from editing fields
        # they don't need or we don't want them to have.
        # Filtered options: 'status', ('publish_date', 'expiry_date'), 'ancestor',
        # 'forum_url', 'forum_vars', 'i18n_ready', 'in_menus', 'login_required', 'in_sitemap'
        # TODO: Only super admins should have in_sitemap as an option. It removes the curriculum from the Pages List
        if self.can_access_all(request):
            general_fields = ['title', 'status', ('publish_date', 'expiry_date'), 'content', 'ancestor',
                              'gradeband', 'assessment_commentary', 'version', 'unit_numbering', 'auto_forum',
                              'support_script', 'display_questions','feedback_url', 'feedback_vars',
                              'unit_template_override','canonical_slug', 'frameworks', 'in_menus', 'login_required']
            meta_data_fields = ['_meta_title', 'slug', ('description', 'gen_description'), 'keywords', 'in_sitemap']
        else:
            general_fields = ['title', 'content',
                              'gradeband', 'assessment_commentary', 'unit_numbering',
                              'unit_template_override', 'canonical_slug', 'frameworks']
            meta_data_fields = ['_meta_title', 'slug', ('description', 'gen_description'), 'keywords']

        fieldsets = (
            (None, {
                'fields': general_fields
            }),
            ('Meta data', {
                'fields': meta_data_fields,
                'classes': ('collapse-closed',)})
        )
        return fieldsets

class UnitAdmin(PageAdmin, VersionAdmin, FilterableAdmin):
    model = Unit
    inlines = (TopicInline,)

    def can_access_all(self, request):
        return request.user.has_perm('curricula.access_all_units')

    def get_fieldsets(self, request, obj=None):

        # Use the access_all permission to exclude partners from editing fields
        # they don't need or we don't want them to have.
        # Filtered options: 'status', ('publish_date', 'expiry_date'), 'ancestor',
        # 'forum_url', 'forum_vars', 'i18n_ready', 'in_menus', 'login_required', 'in_sitemap'
        # TODO: Only super admins should have in_sitemap as an option. It removes the curriculum from the Pages List
        if self.can_access_all(request):
            general_fields = ['title', 'status', ('publish_date', 'expiry_date'), 'content', 'ancestor',
                           'disable_numbering', 'number', 'stage_name', 'questions', 'assessment_commentary',
                           'show_calendar', 'week_length', 'forum_url', 'forum_vars', 'lesson_template_override',
                           'i18n_ready', 'in_menus', 'login_required']
            meta_data_fields = ['_meta_title', 'slug', ('description', 'gen_description'), 'keywords', 'in_sitemap']
        else:
            general_fields = ['title', 'content',
                           'disable_numbering', 'number', 'stage_name', 'questions', 'assessment_commentary',
                           'show_calendar', 'week_length', 'lesson_template_override']
            meta_data_fields = ['_meta_title', 'slug', ('description', 'gen_description'), 'keywords']

        fieldsets = (
            (None, {
                'fields': general_fields
            }),
            ('Meta data', {
                'fields': meta_data_fields,
                'classes': ('collapse-closed',)})
        )
        return fieldsets


class ChapterAdmin(PageAdmin, FilterableAdmin):
    model = Chapter
    filter_horizontal = ('understandings',)
    inlines = (TopicInline,)

    fieldsets = (
        (None, {
            'fields': ['title', 'status', 'content', 'questions', 'understandings'],
        }),
    )

    def can_access_all(self, request):
        return request.user.has_perm('curricula.access_all_chapters')


'''
UnitStandards allows for quick standards aligning without the ability to edit actual lesson content
'''


class UnitStandardsForm(ModelForm):
    class Meta:
        model = Unit
        fields = ('title',)


class UnitStandards(Unit):
    class Meta:
        proxy = True
        verbose_name = u'Unit Standards'
        verbose_name_plural = u'Unit Standards'


class UnitStandardsAdmin(ImportExportModelAdmin):
    list_display = ('title', 'curriculum', 'number')
    list_filter = ('curriculum', 'curriculum__version')
    list_editable = ()
    readonly_fields = ('title',)
    inlines = (LessonStandardsInline,)
    form = UnitStandardsForm

    def get_changelist_form(self, request, **kwargs):
        return UnitStandardsForm

admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(UnitStandards, UnitStandardsAdmin)
# admin.site.register(UnitLesson)

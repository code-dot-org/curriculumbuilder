from django.db import models
from django.db.models import Count, Q

from i18n.models import Internationalizable

from itertools import chain

"""
Top level of a standards framework

"""


class Framework(Internationalizable):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    website = models.URLField()

    def __unicode__(self):
        return self.name

    @property
    def top_categories(self):
        return self.categories.top()

    @classmethod
    def get_i18n_objects(cls):
        return (
            super(Framework, cls)
            .get_i18n_objects()
            .prefetch_related(
                'standards',
                'standards__anchors',
                'standards__anchors__unit',
                'standards__lesson_set',
                'standards__lesson_set__unit',
                'standards__opportunities',
                'standards__opportunities__unit'
            )
        )

    @property
    def should_be_translated(self):
        return any(standard.should_be_translated for standard in self.standards.all())

    @classmethod
    def internationalizable_fields(cls):
        return ['name', 'description']


"""
Generic standards category to allow for various
standards framework structures.
Can be related to another upstream category,
or a Framework if this is the top level category.

Type should be set to the name appropriate for each framework

"""


class CategoryQuerySet(models.QuerySet):
    def top(self):
        return self.filter(parent=None)

    def bottom(self):
        return self.filter(standards__isnull=False).distinct()


class Category(Internationalizable):
    name = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    framework = models.ForeignKey(Framework, blank=True, null=True, related_name="categories")
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children")

    def __unicode__(self):
        # When importing via django-import-export, categories may be listed before the framework is assigned
        if self.framework:
            return "%s %s: %s" % (self.framework.slug, self.shortcode, self.name)
        else:
            return self.shortcode

    class Meta:
        ordering = ['framework', 'shortcode']
        verbose_name_plural = "categories"

    def child_standards(self):
        return Standard.objects.filter(Q(category=self) | Q(category__parent=self))

    objects = CategoryQuerySet.as_manager()

    def parent_shortcode(self):
        return self.parent.shortcode if self.parent else None

    @classmethod
    def get_i18n_objects(cls):
        return (
            super(Category, cls)
            .get_i18n_objects()
            .prefetch_related(
                'standards',
                'standards__anchors',
                'standards__anchors__unit',
                'standards__lesson_set',
                'standards__lesson_set__unit',
                'standards__opportunities',
                'standards__opportunities__unit'
            )
        )

    @property
    def should_be_translated(self):
        return any(standard.should_be_translated for standard in self.standards.all())

    @classmethod
    def internationalizable_fields(cls):
        return ['name', 'description']



"""
Individual grades which make up a GradeBand

"""


class Grade(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


"""
A collection of grades to which a standard can belong

"""


class GradeBand(Internationalizable):
    name = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    grades = models.ManyToManyField(Grade)

    def __unicode__(self):
        return self.name

    @classmethod
    def get_i18n_objects(cls):
        return (
            super(GradeBand, cls)
            .get_i18n_objects()
            .prefetch_related(
                'standards',
                'standards__anchors',
                'standards__anchors__unit',
                'standards__lesson_set',
                'standards__lesson_set__unit',
                'standards__opportunities',
                'standards__opportunities__unit'
            )
        )

    @property
    def should_be_translated(self):
        return any(standard.should_be_translated for standard in self.standards.all())

    @classmethod
    def internationalizable_fields(cls):
        return ['name', 'description']


"""
Standards

"""


class Standard(Internationalizable):
    name = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    gradeband = models.ForeignKey(GradeBand, related_name='standards')
    category = models.ForeignKey(Category, related_name='standards')
    framework = models.ForeignKey(Framework, blank=True, null=True, related_name='standards')
    slug = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        # return self.slug
        return "%s: %s" % (self.slug, self.name)

    @classmethod
    def get_i18n_objects(cls):
        return (
            super(Standard, cls)
            .get_i18n_objects()
            .prefetch_related(
                'anchors',
                'anchors__unit',
                'lesson_set',
                'lesson_set__unit',
                'opportunities',
                'opportunities__unit'
            )
        )

    @property
    def should_be_translated(self):
        related_lessons = set(chain(self.anchors.all(), self.lesson_set.all(), self.opportunities.all()))
        return any(lesson.should_be_translated for lesson in related_lessons)

    @classmethod
    def internationalizable_fields(cls):
        return ['name', 'description']

    class Meta:
        ordering = ['framework', 'category', 'slug']

    def save(self, *args, **kwargs):
        self.name = self.name[:255]
        self.framework = self.get_framework()
        '''
        if self.framework.slug == 'CSTA':
          self.shortcode = self.category.shortcode + '.' + self.gradeband.shortcode + ':' + self.shortcode
        elif self.framework.slug == 'ISTE':
          self.shortcode = self.category.shortcode + '.' + self.shortcode
        '''

        self.slug = self.get_slug()
        super(Standard, self).save(*args, **kwargs)

    @property
    def top_category(self):
        category = self.category
        while category.parent:
            category = category.parent

        return category

    def get_framework(self):
        try:
            category = self.category
        except:
            print "Couldn't find category"
            return

        while not hasattr(category, 'framework'):
            category = category.category
        return category.framework

    def get_slug(self):
        try:
            framework = self.framework
            '''
            if framework.slug == 'CSTA':
              return self.category.shortcode + '.' + self.gradeband.shortcode + ':' + self.shortcode
            elif framework.slug == 'ISTE':
              return framework.slug + self.category.shortcode + '.' + self.shortcode
            else:
              return framework.slug + '-' + self.shortcode
            '''
            return framework.slug + '-' + self.shortcode
        except:
            return self.shortcode

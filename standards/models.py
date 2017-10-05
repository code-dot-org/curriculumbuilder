from django.db import models
from django.db.models import Count, Q

"""
Top level of a standards framework

"""


class Framework(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    website = models.URLField()

    def __unicode__(self):
        return self.name

    @property
    def top_categories(self):
        return self.categories.top()


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


class Category(models.Model):
    name = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    framework = models.ForeignKey(Framework, blank=True, null=True, related_name="categories")
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children")

    def __unicode__(self):
        return "%s %s: %s" % (self.framework.slug, self.shortcode, self.name)

    class Meta:
        ordering = ['framework', 'shortcode']
        verbose_name_plural = "categories"

    def child_standards(self):
        return Standard.objects.filter(Q(category=self) | Q(category__parent=self))

    objects = CategoryQuerySet.as_manager()



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


class GradeBand(models.Model):
    name = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    grades = models.ManyToManyField(Grade)

    def __unicode__(self):
        return self.name


"""
Standards

"""


class Standard(models.Model):
    name = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    gradeband = models.ForeignKey(GradeBand)
    category = models.ForeignKey(Category, related_name='standards')
    framework = models.ForeignKey(Framework, blank=True, null=True, related_name='standards')
    slug = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        # return self.slug
        return "%s: %s" % (self.slug, self.name)

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

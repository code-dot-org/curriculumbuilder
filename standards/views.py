import operator
import json

import unicodecsv as csv

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from curricula.models import Curriculum, Unit
from standards.models import *
from standards.serializers import *


def index(request):
    frameworks = Framework.objects.all()
    curricula = Curriculum.objects.all()
    return render(request, 'standards/index.html', {'frameworks': frameworks, 'curricula': curricula})


def by_framework(request, slug, curriculum_slug=None):
    framework = get_object_or_404(Framework, slug=slug)
    top_categories = Category.objects.filter(framework=framework, parent__isnull=True) \
        .prefetch_related('children__standards__lesson_set', 'standards__lesson_set')
    return render(request, 'standards/framework.html', {'framework': framework, 'top_categories': top_categories})


def by_curriculum(request, slug):
    curriculum = get_object_or_404(Curriculum, slug=slug)
    '''
    standards_cols, standards_rows = curriculum.get_standards()
    cols = json.dumps(standards_cols)
    cols = cols.replace("\"heatCell\"", "heatCell")
    rows = json.dumps(standards_rows)
    return render(request, 'standards/curriculum.html', {'curriculum': curriculum,
                                                         'standards_cols': cols,
                                                         'standards_rows': rows})
    '''
    return render(request, 'standards/curriculum_nogrid.html', {'curriculum': curriculum})


def by_curriculum_csv(request, slug):
    curriculum = get_object_or_404(Curriculum, slug=slug)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s_standards.csv"' % curriculum.slug

    writer = csv.writer(response, encoding='utf-8')
    writer.writerow([
        'curriculum',
        'unit',
        'lesson #',
        'lesson name',
        'standard framework',
        'standard',
        'category',
        'description',
        'cross curricular opportunity'
    ])
    for unit in curriculum.units:
        for lesson in unit.lessons:
            for standard in lesson.standards.all():
                writer.writerow([
                    curriculum.slug,
                    unit.slug,
                    'lesson %d' % lesson.number,
                    lesson.title,
                    standard.framework.slug,
                    standard.shortcode,
                    standard.category.name,
                    standard.name,
                    False
                ])
            for standard in lesson.opportunity_standards.all():
                writer.writerow([
                    curriculum.slug,
                    unit.slug,
                    'lesson %d' % lesson.number,
                    lesson.title,
                    standard.framework.slug,
                    standard.shortcode,
                    standard.category.name,
                    standard.name,
                    True
                ])
    return response


def by_unit(request, slug, unit_slug):
    curriculum = get_object_or_404(Curriculum, slug=slug)
    unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)
    '''
    standards_cols, standards_rows = unit.get_standards()
    cols = json.dumps(standards_cols)
    cols = cols.replace("\"heatCell\"", "heatCell")
    rows = json.dumps(standards_rows)
    return render(request, 'standards/curriculum.html', {'curriculum': curriculum,
                                                         'unit': unit,
                                                         'standards_cols': cols,
                                                         'standards_rows': rows})
    '''
    return render(request, 'standards/curriculum_nogrid.html', {'curriculum': curriculum, 'unit': unit})


def by_unit_csv(request, slug, unit_slug):
    curriculum = get_object_or_404(Curriculum, slug=slug)
    unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s_%s_standards.csv"' % (curriculum.slug, unit.slug)

    writer = csv.writer(response, encoding='utf-8')
    writer.writerow([
        'curriculum',
        'unit',
        'lesson #',
        'lesson name',
        'standard framework',
        'standard',
        'category',
        'description',
        'cross curricular opportunity'
    ])
    for lesson in unit.lessons:
        for standard in lesson.standards.all():
            writer.writerow([
                curriculum.slug,
                unit.slug,
                'lesson %d' % lesson.number,
                lesson.title,
                standard.framework.slug,
                standard.shortcode,
                standard.category.name,
                standard.name,
                'false'
            ])
        for standard in lesson.opportunity_standards.all():
            writer.writerow([
                curriculum.slug,
                unit.slug,
                'lesson %d' % lesson.number,
                lesson.title,
                standard.framework.slug,
                standard.shortcode,
                standard.category.name,
                standard.name,
                'true'
            ])
    return response


def standards_by_framework_csv(request, slug):
    framework = get_object_or_404(Framework, slug=slug)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s_standards.csv"' % (framework.slug)

    writer = csv.writer(response, encoding='utf-8')
    writer.writerow([
        'framework',
        'category',
        'standard',
        'description'
    ])
    for standard in framework.standards.all():
        writer.writerow([
            framework.slug,
            standard.category.shortcode,
            standard.shortcode,
            standard.name
        ])
    return response


def categories_by_framework_csv(request, slug):
    framework = get_object_or_404(Framework, slug=slug)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s_categories.csv"' % (framework.slug)

    writer = csv.writer(response, encoding='utf-8')
    writer.writerow([
        'framework',
        'parent',
        'category',
        'description'
    ])

    # Make categories without parents appear before categories with parents.
    # Because there are only two layers of categories, this ensures that
    # every parent category appears before any of its children.
    categories = framework.categories.order_by('-parent_id').all()

    for category in categories:
        writer.writerow([
            framework.slug,
            category.parent_shortcode(),
            category.shortcode,
            category.description
        ])
    return response


def single_standard(request, slug, shortcode):
    # standard = get_object_or_404(Standard.objects.prefetch_related('lesson_set__unitlesson_set__unit__curriculum'), framework__slug=slug, shortcode=shortcode)
    standard = get_object_or_404(Standard, framework__slug=slug, shortcode=shortcode)
    return render(request, 'standards/standard.html', {'standard': standard})


@api_view(['GET', ])
def standard_element(request, slug, shortcode, format=None):
    # standard = get_object_or_404(Standard.objects.prefetch_related('lesson_set__unitlesson_set__unit__curriculum'), framework__slug=slug, shortcode=shortcode)
    standard = get_object_or_404(Standard, framework__slug=slug, shortcode=shortcode)

    serializer = StandardSerializer(standard)
    return Response(serializer.data)


@api_view(['GET', ])
def standard_list(request, curriculum_slug, framework_slug=None):
    curriculum = get_object_or_404(Curriculum, slug=curriculum_slug)

    if framework_slug:
        standards = Standard.objects.filter(framework__slug=framework_slug)
    else:
        standards = Standard.objects.all()

    serializer = StandardSerializer(standards, context={'curriculum': curriculum}, many=True)
    return Response(serializer.data)


@api_view(['GET', ])
def nested_standard_list(request, curriculum_slug, framework_slug=None):
    curriculum = get_object_or_404(Curriculum, slug=curriculum_slug)
    query = []
    serialized = {}

    if framework_slug:
        query.append(("framework__slug", framework_slug))

    query_list = [Q(x) for x in query]
    standards = Standard.objects.filter(reduce(operator.and_, query_list)).order_by('shortcode')

    for standard in standards:
        print standard.shortcode
        serializer = NestedStandardSerializer(standard, context={'curriculum': curriculum})
        serialized[standard.shortcode] = serializer.data

    # return Response(serializer.data)
    return Response(SortedDict(serialized))


@api_view(['GET', ])
def nested_category_list(request, curriculum_slug, framework_slug=None):
    curriculum = get_object_or_404(Curriculum, slug=curriculum_slug)
    query = []
    serialized = {}

    if request.GET.get('category'):  # Filter by standard / cat type
        query.append(("type", request.GET.get('category')))
    else:
        query.append(('parent__isnull', True))

    if framework_slug:
        query.append(("framework__slug", framework_slug))
        # categories = Category.objects.filter(parent__isnull=True, framework__slug=framework_slug).order_by('shortcode')
        # else:
        # categories = Category.objects.filter(parent__isnull=True).order_by('shortcode')

    query_list = [Q(x) for x in query]
    categories = Category.objects.filter(reduce(operator.and_, query_list)).order_by('shortcode')

    for category in categories:
        print category.shortcode
        serializer = NestedCategorySerializer(category, context={'curriculum': curriculum})
        serialized[category.shortcode] = serializer.data

    # return Response(serializer.data)
    return Response(SortedDict(serialized))

import os, time, re

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from mezzanine.core.views import edit

from django.core.files.storage import get_storage_class, FileSystemStorage, default_storage
from django.core.files.base import ContentFile

# from wkhtmltopdf import WKHtmlToPdf
from cStringIO import StringIO
import pdfkit
import pycurl
import logging
import json
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from urllib import urlencode
from urllib2 import Request, urlopen
# import dryscrape

from multiurl import ContinueResolving

from ipware.ip import get_real_ip

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import generics
from rest_framework import viewsets

import reversion
from reversion.views import create_revision
from reversion.models import Version

from reversion_compare.forms import SelectDiffForm
from reversion_compare.views import HistoryCompareDetailView

from django_slack import slack_message

from curricula.models import *
from curricula.serializers import *
from curricula.forms import ChangelogForm

from documentation.models import IDE, Block, Map

logger = logging.getLogger(__name__)

pdfkit_config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_BIN)

def index(request):
    if request.user.is_staff:
        curricula = Curriculum.objects.all()
    else:
        curricula = Curriculum.objects.filter(login_required=False)

    return render(request, 'curricula/index.html', {'curricula': curricula})


'''
Core curricula and lesson views

'''


def curriculum_view(request, slug):
    pdf = request.GET.get('pdf', False)
    try:
        curriculum = get_object_or_404(Curriculum, slug=slug)
    except Curriculum.DoesNotExist:
        raise ContinueResolving

    if request.user.is_staff:
        units = Unit.objects.filter(curriculum=curriculum)
    else:
        units = Unit.objects.filter(curriculum=curriculum, login_required=False)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ChangelogForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            with reversion.create_revision():
                changelog_user = User.objects.get(username=settings.CHANGELOG_USER)

                curriculum.save()

                # Store some meta-information.
                reversion.set_user(changelog_user)
                reversion.set_comment(form.cleaned_data['comment'])
            return HttpResponseRedirect(curriculum.get_absolute_url())

    # if a GET (or any other method) we'll create a blank form
    form = ChangelogForm()

    changelog = Version.objects.get_for_object(curriculum).filter(revision__user__username=settings.CHANGELOG_USER)

    return render(request, 'curricula/curriculum.html', {'curriculum': curriculum, 'pdf': pdf, 'units': units,
                                                         'form': form, 'changelog': changelog})


def unit_view(request, slug, unit_slug):
    pdf = request.GET.get('pdf', False)

    try:
        curriculum = get_object_or_404(Curriculum, slug=slug)
    except Curriculum.DoesNotExist:
        raise ContinueResolving

    if request.user.is_staff:
        unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)
    else:
        unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug, login_required=request.user.is_staff)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ChangelogForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            with reversion.create_revision():
                changelog_user = User.objects.get(username=settings.CHANGELOG_USER)

                unit.save()

                # Store some meta-information.
                reversion.set_user(changelog_user)
                reversion.set_comment(form.cleaned_data['comment'])
            return HttpResponseRedirect(unit.get_absolute_url())

    # if a GET (or any other method) we'll create a blank form
    form = ChangelogForm()

    changelog = Version.objects.get_for_object(unit).filter(revision__user__username=settings.CHANGELOG_USER)

    if pdf:
        if curriculum.unit_template_override == 'curricula/pl_unit.html':
            template = 'curricula/pl_unit_lessons.html'
        else:
            template = 'curricula/unit_lessons.html'
    else:
        if curriculum.unit_template_override:
            template = unit.curriculum.unit_template_override
        else:
            template = 'curricula/unit.html'

    return render(request, template, {'curriculum': curriculum, 'unit': unit, 'pdf': pdf,
                                      'form': form, 'changelog': changelog})


def unit_at_a_glance(request, slug, unit_slug):

    try:
        curriculum = get_object_or_404(Curriculum, slug=slug)
    except Curriculum.DoesNotExist:
        raise ContinueResolving

    if request.user.is_staff:
        unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)
    else:
        unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug, login_required=request.user.is_staff)

    return render(request, 'curricula/unit_glance.html', {'curriculum': curriculum, 'unit': unit})


def chapter_view(request, slug, unit_slug, chapter_num):
    pdf = request.GET.get('pdf', False)
    curriculum = get_object_or_404(Curriculum, slug=slug)
    unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)
    chapter = get_object_or_404(Chapter, parent__unit=unit, number=chapter_num)

    return render(request, 'curricula/chapter.html',
                  {'curriculum': curriculum, 'unit': unit, 'chapter': chapter, 'pdf': pdf})


def lesson_view(request, slug, unit_slug, lesson_num, optional_num=False):
    pdf = request.GET.get('pdf', False)
    parent = None
    optional = False

    if optional_num:
        optional = True
        lesson = get_object_or_404(
            Lesson.objects.prefetch_related('standards', 'standards__framework', 'standards__category',
                                            'standards__category__parent',
                                            'anchor_standards__framework', 'page_ptr', 'parent',
                                            'parent__unit', 'parent__unit__curriculum', 'parent__children',
                                            'vocab', 'resources', 'activity_set'),
            unit__slug=unit_slug, unit__curriculum__slug=slug, parent__lesson__number=lesson_num, number=optional_num)
        parent = lesson.parent.lesson
        if hasattr(lesson.parent.parent, 'chapter'):
            chapter = lesson.parent.parent.chapter
        else:
            chapter = None

    else:
        lesson = get_object_or_404(
            Lesson.objects.prefetch_related('standards', 'standards__framework', 'standards__category',
                                            'standards__category__parent',
                                            'anchor_standards__framework', 'page_ptr', 'parent',
                                            'parent__unit', 'parent__unit__curriculum', 'parent__children',
                                            'vocab', 'resources', 'activity_set'),
            unit__slug=unit_slug, unit__curriculum__slug=slug, number=lesson_num, parent__lesson__isnull=True)
        if lesson.parent.content_model == 'chapter':
            chapter = lesson.parent.chapter
        else:
            chapter = None

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ChangelogForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print "trying it"
            with reversion.create_revision():
                if form.cleaned_data['teacher_facing']:
                    changelog_user = User.objects.get(username=settings.CHANGELOG_USER)
                else:
                    changelog_user = User.objects.get(username=settings.FEEDBACK_USER)
                    print 'not teacher facing'

                print changelog_user

                lesson.save()

                # Store some meta-information.
                reversion.set_user(changelog_user)
                reversion.set_comment(form.cleaned_data['comment'])
            return HttpResponseRedirect(lesson.get_absolute_url())

    # if a GET (or any other method) we'll create a blank form
    form = ChangelogForm()

    changelog = Version.objects.get_for_object(lesson).filter(revision__user__username=settings.CHANGELOG_USER)

    if lesson.unit.lesson_template_override:
        template = lesson.unit.lesson_template_override
    else:
        template = 'curricula/codestudiolesson.html'

    return render(request, template,
                  {'curriculum': lesson.curriculum, 'unit': lesson.unit, 'chapter': chapter, 'lesson': lesson,
                   'pdf': pdf, 'parent': parent, 'optional': optional, 'form': form, 'changelog': changelog})


def lesson_markdown(request, slug, unit_slug, lesson_num):
    lesson = get_object_or_404(Lesson, unit__slug=unit_slug, unit__curriculum__slug=slug, number=lesson_num,
                               parent__lesson__isnull=True)

    return render(request, 'curricula/lesson-overview.md', {'lesson': lesson}, content_type='text/markdown')


def lesson_overview(request, slug, unit_slug, lesson_num):
    lesson = get_object_or_404(Lesson, unit__slug=unit_slug, unit__curriculum__slug=slug, number=lesson_num,
                               parent__lesson__isnull=True)

    return render(request, 'curricula/lesson-overview.html', {'lesson': lesson})


'''
Unit List Views
'''


def curriculum_resources(request, slug):

    try:
        curriculum = get_object_or_404(Curriculum, slug=slug)
    except Curriculum.DoesNotExist:
        raise ContinueResolving

    return render(request, 'curricula/list_view.html', {'curriculum': curriculum,
                                                        'list_type': 'Resources',
                                                        'include_template': 'curricula/partials/resource_list.html'})


def unit_resources(request, slug, unit_slug):

    try:
        curriculum = get_object_or_404(Curriculum, slug=slug)
    except Curriculum.DoesNotExist:
        raise ContinueResolving

    unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)
    return render(request, 'curricula/list_view.html', {'curriculum': curriculum,
                                                        'unit': unit,
                                                        'list_type': 'Resources',
                                                        'include_template': 'curricula/partials/resource_list.html'})


def curriculum_vocab(request, slug):

    try:
        curriculum = get_object_or_404(Curriculum, slug=slug)
    except Curriculum.DoesNotExist:
        raise ContinueResolving

    return render(request, 'curricula/list_view.html', {'curriculum': curriculum,
                                                    'list_type': 'Vocab',
                                                    'include_template': 'curricula/partials/vocab_list.html'})


def unit_vocab(request, slug, unit_slug):
    curriculum = get_object_or_404(Curriculum, slug=slug)
    unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)
    return render(request, 'curricula/list_view.html', {'curriculum': curriculum,
                                                    'unit': unit,
                                                    'list_type': 'Vocab',
                                                    'include_template': 'curricula/partials/vocab_list.html'})


def curriculum_code(request, slug):
    curriculum = get_object_or_404(Curriculum, slug=slug)
    return render(request, 'curricula/list_view.html', {'curriculum': curriculum,
                                                   'list_type': 'Introduced Code',
                                                   'include_template': 'curricula/partials/code_list.html'})


def unit_code(request, slug, unit_slug):
    curriculum = get_object_or_404(Curriculum, slug=slug)
    unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)
    return render(request, 'curricula/list_view.html', {'curriculum': curriculum,
                                                   'unit': unit,
                                                   'list_type': 'Introduced Code',
                                                   'include_template': 'curricula/partials/code_list.html'})


'''
PDF rendering views

'''


def lesson_pdf(request, slug, unit_slug, lesson_num):
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.WRITEDATA, buffer)

    lesson = get_object_or_404(Lesson, unit__slug=unit_slug, unit__curriculum__slug=slug, number=lesson_num,
                               parent__lesson__isnull=True)

    try:
        c.setopt(c.URL, get_url_for_pdf(request, lesson.get_absolute_url()) + "?pdf=true")
        c.perform()
        c.close()

        compiled = buffer.getvalue()
    except Exception, e:
        logger.exception('PDF Curling Failed')
        return HttpResponse('PDF Curling Failed', status=500)

    if request.GET.get('html'):  # Allows testing the html output
        response = HttpResponse(compiled)
    else:
        try:
            pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS, configuration=pdfkit_config)
        except Exception:
            logger.exception('PDF Generation Failed')
            return HttpResponse('PDF Generation Failed', status=500)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=lesson.pdf'

        slack_message('slack/message.slack', {
            'message': 'created a PDF from %s %s lesson %s' % (slug, unit_slug, lesson_num),
            'user': request.user.get_username(),
        })

    return response


def unit_compiled(request, slug, unit_slug):

    curriculum = get_object_or_404(Curriculum, slug=slug)
    unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)

    if curriculum.unit_template_override == 'curricula/pl_unit.html':
        template = 'curricula/pl_unit_lessons.html'
    else:
        template = 'curricula/unit_lessons.html'

    return render(request, template, {'curriculum': curriculum, 'unit': unit})


def unit_pdf(request, slug, unit_slug):

    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.WRITEDATA, buffer)

    unit = get_object_or_404(Unit, curriculum__slug=slug, slug=unit_slug)

    try:
        c.setopt(c.URL, get_url_for_pdf(request, unit.get_compiled_url(), True))
        c.perform()

        c.close()
        compiled = buffer.getvalue()
    except Exception:
        logger.exception('PDF Curling Failed')
        return HttpResponse('PDF Curling Failed', status=500)

    if request.GET.get('html'):  # Allows testing the html output
        response = HttpResponse(compiled)
    else:
        try:
            pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS, configuration=pdfkit_config)
        except Exception:
            logger.exception('PDF Generation Failed')
            return HttpResponse('PDF Generation Failed', status=500)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=unit%s.pdf' % unit.number

        ip = get_real_ip(request)
        slack_message('slack/message.slack', {
            'message': 'created a PDF from %s %s' % (slug, unit_slug),
            'user': request.user.get_username() or ip,
        })

    return response


def unit_pjspdf(request, slug, unit_slug):

    output = PdfFileWriter()
    unit = get_object_or_404(Unit, curriculum__slug=slug, slug=unit_slug)

    data = {
        "url": get_url_for_pdf(request, unit.get_absolute_url(), True),
        "renderType": "pdf"
    }

    url = 'http://PhantomJScloud.com/api/browser/v2/%s/' % settings.PHANTOMJS_KEY
    headers = {'content-type': 'application/json'}

    req = Request(url, json.dumps(data), headers)
    response = urlopen(req)
    results = response.read()
    print '\nresponse status code'
    print response.code
    print '\nresponse headers (pay attention to pjsc-* headers)'
    print response.headers

    memoryPDF = StringIO(results)
    localPDF = PdfFileReader(memoryPDF)
    output.appendPagesFromReader(localPDF)

    pdfresponse = HttpResponse(content_type='application/pdf')
    output.write(pdfresponse)
    pdfresponse['Content-Disposition'] = 'inline;filename=unit%s.pdf' % unit.number

    slack_message('slack/message.slack', {
        'message': 'created a PDF from %s %s' % (slug, unit_slug),
        'user': request.user,
    })

    return pdfresponse


def unit_resources_pdf(request, slug, unit_slug):
    merger = PdfFileMerger()
    unit = get_object_or_404(Unit, curriculum__slug=slug, slug=unit_slug)
    for lesson in unit.lessons.exclude(keywords__keyword__slug="optional"):
        lesson_string = render_to_string("curricula/lesson_title.html", {'unit': unit, 'lesson': lesson},
                                         request=request)
        lesson_page = pdfkit.from_string(lesson_string, False, options=settings.WKHTMLTOPDF_CMD_OPTIONS, configuration=pdfkit_config)
        lesson_page_pdf = StringIO(lesson_page)
        merger.append(PdfFileReader(lesson_page_pdf))
        for resource in lesson.resources.all():
            if resource.gd:
                try:
                    remotePDF = urlopen(Request(resource.gd_pdf())).read()
                    memoryPDF = StringIO(remotePDF)
                    localPDF = PdfFileReader(memoryPDF)
                    merger.append(localPDF)
                except Exception:

                    attachments = [
                        {
                            'color': 'danger',
                            'title': 'URL',
                            'text': resource.url,
                        },
                        {
                            'color': 'danger',
                            'title': 'Related Lesson',
                            'text': lesson.get_absolute_url(),
                        },
                    ]

                    ip = get_real_ip(request)

                    slack_message('slack/message.slack', {
                        'message': "tried and failed to publish resource %s - %s (pk %s). "
                                   "Check to ensure that it's a publicly accessible Google Doc"
                                   % (resource.name, resource.type, resource.pk),
                        'user': request.user.get_username() or ip,
                    }, attachments)
                    return HttpResponse('PDF Generation Failed', status=500)

    response = HttpResponse(content_type='application/pdf')
    merger.write(response)
    response['Content-Disposition'] = 'inline;filename=unit%s_resources.pdf' % unit.number

    ip = get_real_ip(request)
    slack_message('slack/message.slack', {
        'message': 'created a resource PDF from %s %s' % (slug, unit_slug),
        'user': request.user.get_username() or ip,
    })

    return response


def curriculum_pdf(request, slug):
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.WRITEDATA, buffer)

    curriculum = get_object_or_404(Curriculum.objects.prefetch_related('unit_set', 'unit_set__children'), slug=slug)

    c.setopt(c.URL, get_url_for_pdf(request, curriculum.get_absolute_url(), False))
    c.perform()

    for unit in curriculum.unit_set.all():
        c.setopt(c.URL, get_url_for_pdf(request, unit.get_absolute_url(), False))
        c.perform()
        for lesson in unit.children.all():
            c.setopt(c.URL, get_url_for_pdf(request, lesson.lesson.get_absolute_url(), False))
            c.perform()

    c.close()
    compiled = buffer.getvalue()

    if request.GET.get('html'):  # Allows testing the html output
        response = HttpResponse(compiled)
    else:
        pdf = pdfkit.from_string(compiled.decode('utf8'), False, options=settings.WKHTMLTOPDF_CMD_OPTIONS, configuration=pdfkit_config)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=curriculum.pdf'
    return response


def get_url_for_pdf(request, abs_url, aws=False):
    # On production we should pull the pages locally to ensure the most recent copy,
    # This causes a crash on local dev, so in that case pull pages from S3

    if aws:  #aws or not settings.ON_PAAS:
        print abs_url
        return settings.AWS_BASE_URL + abs_url
    else:
        return 'http://%s%s?pdf=true' % (get_current_site(request).domain, abs_url)


'''
Publishing views

'''


@staff_member_required
def publish(request):
    try:
        pk = int(request.GET.get('pk'))

        page_type = request.GET.get('type')

        if request.GET.get('lessons') == 'true':
            children = True
        else:
            children = False

        klass = globals()[page_type]

        obj = klass.objects.get(pk=pk)

        if request.GET.get('pdf') == 'true':
            as_pdf = True
            pub_func = obj.publish_pdfs
        else:
            as_pdf = False
            pub_func = obj.publish

        slack_message('slack/message.slack', {
            'message': 'kicked off a publish of %s %s \n With children: %s\n As pdf: %s'
                       % (page_type, obj.title, children, as_pdf),
            'user': request.user,
        })

    except Exception, e:
        logger.exception('Publishing failed')

        return HttpResponse(e.message, content_type='application/json', status=500)

    return StreamingHttpResponse(pub_func(children), content_type='text/event-stream')


@staff_member_required
def old_publish(request):
    try:
        pk = int(request.POST.get('pk'))

        page_type = request.POST.get('type')

        if request.POST.get('lessons') == 'true':
            children = True
        else:
            children = False

        klass = globals()[page_type]

        obj = klass.objects.get(pk=pk)

        if request.POST.get('pdf') == 'true':
            payload = obj.publish_pdfs()
        else:
            payload = obj.publish(children)

        attachments = [
            {
                'color': '#00adbc',
                'title': 'URL',
                'text': obj.get_absolute_url(),
            },
            {
                'color': '#00adbc',
                'title': 'Publishing Details',
                'text': json.dumps(payload),
            },
        ]

        slack_message('slack/message.slack', {
            'message': 'published %s %s' % (page_type, obj.title),
            'user': request.user,
        }, attachments)

    except Exception, e:
        payload = {'status': 500, 'error': 'failed', 'exception': e.message}
        logger.exception('Publishing failed')

    return HttpResponse(json.dumps(payload), content_type='application/json', status=payload.get('status', 200))


@staff_member_required
def get_stage_details(request):
    try:
        pk = int(request.POST.get('pk'))
        lesson = get_object_or_404(Lesson, pk=pk)
        if not hasattr(lesson.unit, 'stage_name'):
            payload = {'error': 'No stage name for unit', 'status': 404}
        else:
            lesson.get_levels_from_levelbuilder()
            payload = {'success': 'true'}
    except Exception, e:
        payload = {'status': 500, 'error': 'failed', 'exception': e.message}
    print payload
    return HttpResponse(json.dumps(payload), content_type='application/json', status=payload.get('status', 200))


'''
Supplemental Admin Views

'''


def page_history(request, page_id):
    page = get_object_or_404(Page, pk=page_id)
    history = Version.objects.get_for_object(page).filter(revision__user__username__in=(settings.CHANGELOG_USER,
                                                                                        settings.FEEDBACK_USER))

    return render(request, 'curricula/page_history.html', {'page': page, 'history': history})


def unit_feedback(request, slug, unit_slug):
    unit = get_object_or_404(Unit, slug=unit_slug, curriculum__slug=slug)
    history = {"L%02d - %s" % (l.number, l.title): [v.revision for v in Version.objects.get_for_object(l)
        .filter(revision__user__username__in=(settings.CHANGELOG_USER,
                                              settings.FEEDBACK_USER))] for l in unit.lesson_set.all()}

    return render(request, 'curricula/unit_feedback.html', {'unit': unit, 'history': sorted(history.items())})


class CompareHistoryView(HistoryCompareDetailView):
    model = Lesson
    template_name = 'curricula/compare_history.html'

    def get_context_data(self, **kwargs):
        context = super(HistoryCompareDetailView, self).get_context_data()
        action_list = self._get_action_list()

        if len(action_list) < 2:
            # Less than two history items aren't enough to compare ;)
            comparable = False
        else:
            comparable = True
            # for pre selecting the compare radio buttons depend on the ordering:
            if self.history_latest_first:
                action_list[0]["first"] = True
                action_list[1]["second"] = True
            else:
                action_list[-1]["first"] = True
                action_list[-2]["second"] = True

        if self.request.GET:
            form = SelectDiffForm(self.request.GET)
            if not form.is_valid():
                msg = "Wrong version IDs."
                raise Http404(msg)

            version_id1 = form.cleaned_data["version_id1"]
            version_id2 = form.cleaned_data["version_id2"]

            if version_id1 > version_id2:
                # Compare always the newest one (#2) with the older one (#1)
                version_id1, version_id2 = version_id2, version_id1

            obj = self.get_object()
            queryset = Version.objects.get_for_object(obj)
            version1 = get_object_or_404(queryset, pk=version_id1)
            version2 = get_object_or_404(queryset, pk=version_id2)
            related1 = version1.revision.version_set.all()
            related2 = version2.revision.version_set.all()

            next_version = queryset.filter(pk__gt=version_id2).last()
            prev_version = queryset.filter(pk__lt=version_id1).first()
            compare_data = []

            compared, has_unfollowed_fields = self.compare(obj, version1, version2)
            compare_data.append(compared)

            for activity in obj.activity_set.all():
                activity_1 = related1.get_for_object(activity).first()
                activity_2 = related2.get_for_object(activity).first()
                print "related obj"
                print activity
                print "related_v1"
                print activity_1
                print "related_v2"
                print activity_2
                if activity_1 and activity_2:
                    compared, fields = self.compare(activity, activity_1, activity_2)
                    compare_data.append(compared)

            context.update({
                "compare_data": compare_data,
                "has_unfollowed_fields": has_unfollowed_fields,
                "version1": version1,
                "version2": version2
            })

            if next_version:
                next_url = "?version_id1=%i&version_id2=%i" % (
                    version2.id, next_version.id
                )
                context.update({'next_url': next_url})
            if prev_version:
                prev_url = "?version_id1=%i&version_id2=%i" % (
                    prev_version.id, version1.id
                )
                context.update({'prev_url': prev_url})

        # Compile the context.
        context.update({
            "action_list": action_list,
            "comparable": comparable,
            "compare_view": True,
        })
        return context


@csrf_exempt
@staff_member_required
def image_upload(request):
    if request.method == 'POST' and request.FILES['file']:
        payload = {}
        status = 200
        newFile = request.FILES['file']
        try:
            fileLocation = os.path.join('uploads', newFile.name)
            newFileName = default_storage.save(fileLocation, newFile)
            payload['filename'] = "%s%s" % (settings.MEDIA_URL, newFileName)
        except Exception:
            logger.exception('Image upload failed')
            payload['error'] = "Failed to upload image"
            status = 400
        return JsonResponse(payload, status=status)


'''
API views

'''


@api_view(['POST', ])
def feedback(request):
    RE_FEEDBACK = "^(?P<curric>\S+)\s{1}(u|U)(?P<unit>\d+)(l|L)(?P<lesson>\d+)\s{1}(?P<msg>.*)"

    user = "@%s" % request.POST.get("user_name", "somebody")
    text = request.POST.get("text")
    details = text

    match = re.match(RE_FEEDBACK, text)
    if match:
        curric_slug = match.group('curric').lower()
        unit_num = int(match.group('unit'))
        lesson_num = int(match.group('lesson'))
        details = match.group('msg')
        lesson = Lesson.objects.filter(curriculum__slug=curric_slug, unit__number=unit_num, number=lesson_num).first()

        if lesson:

            with reversion.create_revision():
                changelog_user = User.objects.get(username=settings.FEEDBACK_USER)

                lesson.save()

                # Store some meta-information.
                reversion.set_user(changelog_user)
                reversion.set_comment(details)
            message = "Feedback recorded for %s: %s: %s." % (lesson.curriculum, lesson.unit, lesson)
            title = "Success!"
        else:
            message = "Unable to find matching lesson."
            title = "Failure :/"
    else:
        message = "Unable to find matching lesson."
        title = "Failure :/"

    attachments = [
        {
            'title': title,
            'color': '#00adbc',
            'text': message
        }
    ]
    payload = {
        "response_type": "in_channel",
        "attachments": attachments,
    }

    return Response(payload, content_type='application/json')


@api_view(['POST', 'GET'])
def arduino(request, command, format=None):
    arduino_url = "http://caldwell.ddns.net/arduino/%s" % command
    arduino_response = urlopen(Request(arduino_url)).read()

    return Response(arduino_response)


@never_cache
def proxy_api(request, api_type, api_args):
    print api_type
    print api_args
    if api_type == 'weather':
        content_type = 'application/json'
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = "select item.condition from weather.forecast where woeid in " \
                    "(select woeid from geo.places(1) where text = '%s')" % api_args
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        print result

        try:
            data = json.loads(result)
            data = data['query']['results']['channel']['item']['condition']
            print data
        except:
            data = {'error': 'failed'}
            print data

        data = json.dumps(data)
    if api_type == 'temperature':
        content_type = 'text/plain'
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = "select item.condition from weather.forecast where woeid in " \
                    "(select woeid from geo.places(1) where text = '%s')" % api_args
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        print result

        try:
            data = json.loads(result)
            data = data['query']['results']['channel']['item']['condition']['temp']
            data = "%sF" % data
        except:
            data = 'error'
            print data

    return HttpResponse(data, content_type=content_type)


@api_view(['GET', ])
def curriculum_list(request, format=None):
    curricula = Curriculum.objects.all()
    serializer = CurriculumSerializer(curricula, many=True)
    return Response(serializer.data)


@api_view(['GET', ])
def curriculum_element(request, slug, format=None):
    curriculum = get_object_or_404(Curriculum, slug=slug)

    serializer = CurriculumSerializer(curriculum)
    return Response(serializer.data)


@api_view(['GET', ])
def unit_list(request, slug, format=None):
    curriculum = get_object_or_404(Curriculum, slug=slug)

    units = curriculum.units
    serializer = UnitSerializer(units, many=True)
    return Response(serializer.data)


@api_view(['GET', ])
def unit_element(request, slug, unit_slug, format=None):
    curriculum = get_object_or_404(Curriculum, slug=slug)

    unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)

    serializer = UnitSerializer(unit)
    return Response(serializer.data)


@api_view(['GET', ])
def stage_element(request, stage, format=None):
    try:
        unit = Unit.objects.get(login_required=False, status=2, stage_name=stage)
    except MultipleObjectsReturned:
        logger.exception("Warning - found multiple units referencing the stage %s" % stage)
        unit = Unit.objects.filter(login_required=False, status=2, stage_name=stage).first()

    serializer = UnitSerializer(unit)
    return Response(serializer.data)


@api_view(['GET', ])
def api_root(request, format=None):
    return Response({
        'curriculum': reverse('curriculum_list', request=request, format=format)
    })


@api_view(['GET', ])
def lesson_element(request, slug, unit_slug, lesson_num):
    curriculum = get_object_or_404(Curriculum, slug=slug)

    unit = get_object_or_404(Unit, curriculum=curriculum, slug=unit_slug)
    lesson = get_object_or_404(Lesson.objects.prefetch_related('standards__framework', 'anchor_standards__framework',
                                                               'vocab', 'resources', 'activity_set'),
                               parent=unit, _order=int(lesson_num) - 1)

    serializer = LessonSerializer(lesson)
    return Response(serializer.data)


'''
class AnnotationList(generics.ListCreateAPIView):
  queryset = Annotation.objects.all()
  serializer_class = AnnotationSerializer

class AnnotationMember(generics.RetrieveUpdateDestroyAPIView):
  queryset = Annotation.objects.all()
  serializer_class = AnnotationSerializer
'''


class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer


class AnnotationListCreateView(generics.ListCreateAPIView):
    queryset = Annotation.objects.all()
    filter_fields = ('uri', 'owner', 'lesson')
    serializer_class = AnnotationSerializer


class AnnotationSearchView(generics.ListCreateAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def list(self, request):
        lesson = self.request.query_params.get('lesson', None)

        if lesson is None:
            return Response({"Require lesson to filter results"})
        else:
            queryset = Annotation.objects.filter(lesson=lesson)
            serializer = AnnotationSerializer(queryset, many=True)
            return Response({'rows': serializer.data, 'total': len(serializer.data)})


class AnnotationReadUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer


@create_revision()
def reversion_edit(request):
    if request.POST.get("model") == "activity":
        reversion.set_comment("Changed activity %s from frontend" % request.POST.get("name", ''))
    else:
        reversion.set_comment("Changed %s of %s from frontend" % (request.POST.get("fields"),
                                                                  request.POST.get("model")))
    response = edit(request)
    return response

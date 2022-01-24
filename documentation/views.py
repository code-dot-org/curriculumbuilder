from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponseServerError

import logging

from multiurl import ContinueResolving
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mezzanine.pages.models import Page

from models import IDE, Block, Map
from serializers import *

from django.core.exceptions import MultipleObjectsReturned
from rest_framework.decorators import api_view
from rest_framework.response import Response

logger = logging.getLogger(__name__)

def index(request):
    ides = IDE.objects.all()
    maps = Map.objects.all()
    return render(request, 'documentation/index.html', {'ides': ides, 'maps': maps})

def ide_view(request, slug):
    try:
        ide = IDE.objects.get(slug=slug)
    except IDE.DoesNotExist:
        raise ContinueResolving

    return render(request, 'documentation/ide.html', {'ide': ide})


def block_view(request, slug, ide_slug):
    try:
        ide = IDE.objects.get(slug=ide_slug)
    except IDE.DoesNotExist:
        raise ContinueResolving

    try:
        block = Block.objects.get(slug=slug, parent_ide=ide)
    except Block.DoesNotExist:
        raise ContinueResolving

    return render(request, 'documentation/block.html', {'code_block': block, 'ide': ide})


def embed_view(request, slug, ide_slug):
    try:
        ide = IDE.objects.get(slug=ide_slug)
    except IDE.DoesNotExist:
        raise ContinueResolving

    try:
        block = Block.objects.get(slug=slug, parent_ide=ide)
    except Block.DoesNotExist:
        raise ContinueResolving

    return render(request, 'documentation/embed.html', {'code_block': block, 'ide': ide})


def page_view(request, parents, slug):

    if parents == '':
        # Not not under a map parent, look for a top level map under the
        # concepts page
        pages = Map.objects.filter(slug=slug, parent__slug='concepts')
    else:
        # Otherwise look up by the nearest parent
        parent_slug = parents.split('/')[-1]
        pages = Map.objects.filter(slug=slug, parent__slug=parent_slug)

    if pages.count() == 0:
        return HttpResponseNotFound()
    elif pages.count() > 1:
        return HttpResponseServerError("<p>Multiple maps share the same slug "
                                       "%s</p>" % ["<a href='%s'>%s</a>" % (p.get_admin_url(), p.id) for p in pages])

    page = pages.first()

    return render(request, 'documentation/page.html', {'page': page})


def map_view(request, slug):
    try:
        page = Map.objects.get(slug=slug)
    except Map.DoesNotExist:
        raise ContinueResolving

    maps = Map.objects.filter(parent__slug='concepts')

    return render(request, 'documentation/map.html', {'map': page, 'maps': maps})


def maps_view(request, ):
    maps = Map.objects.filter(parent__slug='concepts')
    page = Page.objects.get(slug='concepts')
    return render(request, 'documentation/pages.html', {'page': page, 'pages': maps, 'type': 'Maps'})

@api_view(['GET', ])
def map_export(request, slug):
    page = get_object_or_404(Map, slug=slug)
    serializer = MapExportSerializer(page)
    return Response(serializer.data)

@api_view(['GET', ])
def block_export(request, block_slug, ide_slug, format=None):
    try:
        ide = IDE.objects.get(slug=ide_slug)
    except IDE.DoesNotExist:
        raise ContinueResolving

    try:
        block = get_object_or_404(Block, login_required=False, status=2, slug=block_slug, parent_ide=ide)
    except MultipleObjectsReturned:
        logger.exception("Warning - found multiple blocks referencing the block %s with id %s" % (block_slug, ide_slug))
        block = Block.objects.filter(login_required=False, status=2, block_slug=block_slug, parent_ide=ide).first()

    serializer = BlockExportSerializer(block)
    return Response(serializer.data)

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponseServerError

from multiurl import ContinueResolving

from mezzanine.pages.models import Page

from models import IDE, Block, Map
from curricula.models import Curriculum


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

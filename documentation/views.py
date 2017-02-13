from django.shortcuts import render, get_object_or_404
from mezzanine.pages.models import RichTextPage
from models import IDE, Block


def ide_view(request, slug):
    ide = get_object_or_404(IDE, slug=slug)
    return render(request, 'documentation/ide.html', {'ide': ide})


def block_view(request, slug, ide_slug):
    ide = get_object_or_404(IDE, slug=ide_slug)
    block = get_object_or_404(Block, slug=slug, IDE=ide)
    return render(request, 'documentation/block.html', {'code_block': block, 'ide': ide})


def embed_view(request, slug, ide_slug):
    ide = get_object_or_404(IDE, slug=ide_slug)
    block = get_object_or_404(Block, slug=slug, IDE=ide)
    return render(request, 'documentation/embed.html', {'code_block': block, 'ide': ide})


def page_view(request, slug, curric_slug):
    page = get_object_or_404(RichTextPage, slug=slug, parent__slug=curric_slug)
    return render(request, 'curricula/page.html', {'page': page})

from django.shortcuts import render, get_object_or_404

from models import IDE, Block


def ide_view(request, slug):
    ide = get_object_or_404(IDE, slug=slug)
    return render(request, 'documentation/ide.html', {'ide': ide})


def block_view(request, slug, ide_slug):
    block = get_object_or_404(Block, slug=slug, IDE__slug=ide_slug)
    return render(request, 'documentation/block.html', {'code_block': block})

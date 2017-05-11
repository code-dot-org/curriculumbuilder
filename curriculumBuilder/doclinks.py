from django.db.models import Q

import re

from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree

from documentation.models import Block

DOC_RE = r'(\`)((?P<ide>\w*?)\/)*(?P<block>.*?)(\`)'


class AttrTagPattern(Pattern):
    """
    Return element of type `tag` with a text attribute of group(3)
    of a Pattern and with the html attributes defined with the constructor.

    """

    def __init__(self, pattern, tag, attrs):
        Pattern.__init__(self, pattern)
        self.tag = tag
        self.attrs = attrs

    def handleMatch(self, m):
        el = etree.Element(self.tag)
        el.text = m.group(3)

        block = None
        block_full = m.group('block')
        block_alphanum = re.sub(r'[\(|\{].*[\)|\}\;]', '', m.group('block'))

        if m.group('ide'):
            try:
                block = Block.objects.get(IDE__slug=m.group('ide'), slug=block_full)
            except Block.DoesNotExist:
                try:
                    print "Block with IDE not found, trying by title"
                    block = Block.objects.get(IDE__slug=m.group('ide'), title=block_full)
                except Block.DoesNotExist:
                    print "Block with IDE not found, trying with alphanum only"
                    block = Block.objects.filter(Q(IDE__slug=m.group('ide'), slug=block_alphanum) |
                                                 Q(IDE__slug=m.group('ide'), title=block_alphanum)).first()

        if not block:
            block = Block.objects.filter(Q(slug=block_full) | Q(title=block_full)).first()
            if not block:
                block = Block.objects.filter(Q(slug=block_alphanum) | Q(title=block_alphanum)).first()

        if block:
            el.set('class', 'block')
            el.set('style', 'background-color: %s;' % block.category.color)
            el.text = "<a href='%s'>%s</a>" % (block.get_published_url(), self.escape(m.group('block')))
        else:
            el.text = "%s%s" % (m.group('ide') or '', self.escape(m.group('block')) or '')

        for (key, val) in self.attrs.items():
            el.set(key, val)
        return el

    def escape(self, html):
        """ Basic html escaping """
        html = html.replace('&', '&amp;')
        html = html.replace('<', '&lt;')
        html = html.replace('>', '&gt;')
        return html.replace('"', '&quot;')


class DocLinksExtensions(Extension):
    def extendMarkdown(self, md, md_globals):
        doc_tag = AttrTagPattern(DOC_RE, 'code', {})
        md.inlinePatterns.add('block', doc_tag, '_begin')


def makeExtension(configs=[]):
    return DocLinksExtensions(configs=configs)

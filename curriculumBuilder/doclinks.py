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
        print("IDE:")
        print(m.group('ide'))
        print("Block:")
        print(m.group('block'))

        try:
            block = Block.objects.get(IDE__slug=m.group('ide'), slug=m.group('block'))
        except Block.DoesNotExist:
            try:
                print "Block with IDE not found, trying by title"
                block = Block.objects.get(IDE__slug=m.group('ide'), title__icontains=m.group('block'))
            except Block.DoesNotExist:
                print "Block with IDE not found, trying without"
                block = Block.objects.filter(slug=m.group('block')).first()
                if not block:
                    "Block without IDE not found, trying by title"
                    block = Block.objects.filter(title__icontains=m.group('block')).first()
        if block:
            el.set('class', 'block')
            el.set('style', 'background-color: %s;' % block.category.color)
            el.text = "<a href='%s'>%s</a>" % (block.get_published_url(), block.title)
        else:
            el.text = m.group('block')

        for (key, val) in self.attrs.items():
            el.set(key, val)
        return el


class DocLinksExtensions(Extension):
    def extendMarkdown(self, md, md_globals):
        doc_tag = AttrTagPattern(DOC_RE, 'code', {})
        md.inlinePatterns.add('block', doc_tag, '_begin')


def makeExtension(configs=[]):
    return DocLinksExtensions(configs=configs)

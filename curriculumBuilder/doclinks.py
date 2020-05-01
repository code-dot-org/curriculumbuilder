import urllib

from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree

DOC_RE = r'(\`)((?P<ide>\w*?)\/)*(?P<block>.*?)(\`)'


class DoclinkPattern(Pattern):
    def handleMatch(self, m):
        el = etree.Element("a")
        # we could use django to build these urls more robustly, but since we
        # want to convert this to a clientside renderer anyway, I'm inclined to
        # keep it super simple for now.
        href = "/docs/doclink"
        if (m.group('ide')):
            href += "/{}".format(m.group('ide'))
        href += "/{}".format(m.group('block'))
        href = urllib.quote(href)
        el.set('href', href)
        return el


class DocLinksExtensions(Extension):
    def extendMarkdown(self, md, md_globals):
        doc_tag = DoclinkPattern(DOC_RE)
        md.inlinePatterns.add('block', doc_tag, '_begin')


def makeExtension(configs=[]):
    return DocLinksExtensions(configs=configs)

from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree

CODESTUDIO_RE = r'(\[code-studio\s*)(?P<start>\d+)?-?(?P<end>\d+)?\]'


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
        start = m.group('start')
        end = m.group('end')

        if start is not None:
            el.set('data-start', start)

        if end is not None:
            el.set('data-end', end)

        for (key, val) in self.attrs.items():
            el.set(key, val)
        return el


class CodeStudioExtensions(Extension):
    def extendMarkdown(self, md, md_globals):
        code_studio_tag = AttrTagPattern(CODESTUDIO_RE, 'div', {'class': 'stage_guide'})
        md.inlinePatterns.add('codestudio', code_studio_tag, '_begin')


def makeExtension(configs=[]):
    return CodeStudioExtensions(configs=configs)

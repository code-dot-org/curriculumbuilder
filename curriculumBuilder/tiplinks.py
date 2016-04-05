from markdown.util import etree
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import Pattern

TIPLINK_RE = r'(?:^|\n)?([\w\-]+)!!!\ ?([\w\-]+)?'

class TipLinksExtensions(Extension):
  def extendMarkdown(self, md, md_globals):
    tiplink_tag = TipTagPattern(TIPLINK_RE, 'a', {})
    md.inlinePatterns.add('tiplink', tiplink_tag, '_begin')

class TipTagPattern(Pattern):
  """
  Return element of type `tag` with a text attribute of group(3)
  of a Pattern and with the html attributes defined with the constructor.

  """
  def __init__ (self, pattern, tag, attrs):
    Pattern.__init__(self, pattern)
    self.tag = tag
    self.attrs = attrs

  def handleMatch(self, m):
    tip_type = m.group(2)
    tip_link = m.group(3)
    el = etree.Element(self.tag)
    el.set('href', '#%s_%s' % (tip_type, tip_link))
    el.set('class', 'tiplink tiplink-%s' % (tip_type))
    if tip_type == 'tip':
      el.text = '<i class="glyphicon glyphicon-alert"></i>'
    elif tip_type == 'discussion':
      el.text = '<i class="glyphicon glyphicon-comment"></i>'
    elif tip_type == 'content':
      el.text = '<i class="glyphicon glyphicon-education"></i>'
    else:
      el.text = '<i class="glyphicon glyphicon-alert"></i>'

    for (key,val) in self.attrs.items():
      el.set(key,val)
    return el
def makeExtension(configs=[]):
  return TipLinksExtensions(configs=configs)
from markdown.util import etree
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern

TIPLINK_RE = r'(?:^|\n)?([\w\-]+)!!!\ ?([\w\-]+)?'

class TipLinksExtensions(Extension):
  def extendMarkdown(self, md, md_globals):
    tiplink_tag = TipTagPattern(TIPLINK_RE, 'div', {})
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
    el.set('class', 'tiplink tiplink-%s' % (tip_type))
    if tip_type == 'tip':
      el.text = '<a href="#%s_%s"><i class="glyphicon glyphicon-alert"></i></a>' % (tip_type, tip_link)
    elif tip_type == 'discussion':
      el.text = '<a href="#%s_%s"><i class="glyphicon glyphicon-comment"></i></a>' % (tip_type, tip_link)
    elif tip_type == 'content':
      el.text = '<a href="#%s_%s"><i class="glyphicon glyphicon-education"></i></a>' % (tip_type, tip_link)
    else:
      el.text = '<a href="#%s_%s"><i class="glyphicon glyphicon-alert"></i></a>' % (tip_type, tip_link)

    for (key,val) in self.attrs.items():
      el.set(key,val)
    return el
def makeExtension(configs=[]):
  return TipLinksExtensions(configs=configs)
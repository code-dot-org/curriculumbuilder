from markdown.util import etree
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern

from lessons.models import Vocab

VOCAB_RE = r'(\[v )(.*?)\]'

class AttrTagPattern(Pattern):
  """
  Return element of type `tag` with a text attribute of group(3)
  of a Pattern and with the html attributes defined with the constructor.

  """
  def __init__ (self, pattern, tag, attrs):
    Pattern.__init__(self, pattern)
    self.tag = tag
    self.attrs = attrs

  def handleMatch(self, m):
    el = etree.Element(self.tag)
    el.text = m.group(3)

    try:
      vocab = Vocab.objects.get(word = el.text)
      el.set('title', '%s: %s' % (vocab.word, vocab.detailDef))

    except Vocab.DoesNotExist:
      print "couldn't find that vocab word"
      vocab = Vocab.objects.filter(word__icontains=el.text).first()
      if vocab:
        el.set('title', '%s: %s' % (vocab.word, vocab.detailDef))
      else:
        return el

    for (key,val) in self.attrs.items():
      print 'key ' + key
      print 'value ' + val
      el.set(key,val)
    return el

class VocabLinksExtensions(Extension):
  def extendMarkdown(self, md, md_globals):
    vocab_tag = AttrTagPattern(VOCAB_RE, 'span',{'class':'vocab'})
    md.inlinePatterns.add('vocab', vocab_tag, '_begin')

def makeExtension(configs=[]):
  return VocabLinksExtensions(configs=configs)
from markdown.util import etree
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern

from lessons.models import Resource

RESOURCE_RE = r'(\[r )(.*?)\]'

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
      resource = Resource.objects.get(slug=el.text)
      el.set('href', resource.fallback_url())
      el.text = str(resource)

    except Resource.DoesNotExist:
      print "slug not found, trying name"
      try:
        resource = Resource.objects.get(name=el.text)
        el.set('href', resource.fallback_url())
        el.text = str(resource)

      except Resource.DoesNotExist:
        print "couldn't find by name either!"
        el.text = "Resource not found"

    for (key,val) in self.attrs.items():
      el.set(key,val)
    return el

class ResourceLinksExtensions(Extension):
  def extendMarkdown(self, md, md_globals):
    # resource = Resource.objects.get
    resource_tag = AttrTagPattern(RESOURCE_RE, 'a',{'class':'resource', 'target':'_blank'})
    md.inlinePatterns.add('resource', resource_tag, '_begin')

def makeExtension(configs=[]):
  return ResourceLinksExtensions(configs=configs)
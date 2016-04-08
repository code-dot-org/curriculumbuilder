"""
Based on the Admonition extension for Python-Markdown
========================================

Adds rST-style admonitions. Inspired by [rST][] feature with the same name.

[rST]: http://docutils.sourceforge.net/docs/ref/rst/directives.html#specific-admonitions  # noqa

See <https://pythonhosted.org/Markdown/extensions/admonition.html>
for documentation.

Original code Copyright [Tiago Serafim](http://www.tiagoserafim.com/).

All changes Copyright The Python Markdown Project

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)

"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import re


class TipsExtension(Extension):
  """ Admonition extension for Python-Markdown. """

  def extendMarkdown(self, md, md_globals):
    """ Add Admonition to Markdown instance. """
    md.registerExtension(self)

    md.parser.blockprocessors.add('admonition',
                                  TipsProcessor(md.parser),
                                  '_begin')


class TipsProcessor(BlockProcessor):

  CLASSNAME = 'admonition'
  CLASSNAME_TITLE = 'admonition-title'
  RE = re.compile(r'(?:^|\n)!!!\ ?([\w\-]+)(?:\ "(.*?)")?(?:\ <(.*?)>)?')

  def test(self, parent, block):
    sibling = self.lastChild(parent)
    return self.RE.search(block) or \
           (block.startswith(' ' * self.tab_length) and sibling is not None and
            sibling.get('class', '').find(self.CLASSNAME) != -1)

  def run(self, parent, blocks):
    sibling = self.lastChild(parent)
    block = blocks.pop(0)
    m = self.RE.search(block)

    if m:
      block = block[m.end() + 1:]  # removes the first line

    block, theRest = self.detab(block)

    if m:
      klass, title, anchor, icon = self.get_class_and_title(m)
      div = etree.SubElement(parent, 'div')
      div.set('class', '%s %s' % (self.CLASSNAME, klass))
      if title:
        p = etree.SubElement(div, 'p')
        p.text = '%s%s' % (icon, title)
        p.set('class', self.CLASSNAME_TITLE)
        p.set('id', '%s_%s' % (klass, anchor))
    else:
      div = sibling
      
    content = etree.SubElement(div, 'div')

    self.parser.parseChunk(content, block)

    if theRest:
      # This block contained unindented line(s) after the first indented
      # line. Insert these lines as the first block of the master blocks
      # list for future processing.
      blocks.insert(0, theRest)

  def get_class_and_title(self, match):
    klass, title, anchor, icon = match.group(1).lower(), match.group(2), match.group(3), ''

    if klass == 'tip':
      new_title = 'Teaching Tip'
      icon = '<i class="glyphicon glyphicon-alert"></i>'
    elif klass == 'discussion':
      new_title = 'Discussion Goal'
      icon = '<i class="glyphicon glyphicon-comment"></i>'
    elif klass == 'content':
      new_title = 'Content Corner'
      icon = '<i class="glyphicon glyphicon-education"></i>'
    elif klass =='say':
      new_title = 'Remarks'
      icon = '<i class="fa fa-microphone"></i>'
    elif klass =='guide':
      new_title = None
      icon = '<i class="fa fa-pencil-square-o"></i>'
    else:
      new_title = klass.capitalize()
      icon = ''
    if title is None:
      title = new_title
    elif title == '':
      # an explicit blank title should not be rendered
      # e.g.: `!!! warning ""` will *not* render `p` with a title
      title = None
    return klass, title, anchor, icon


def makeExtension(*args, **kwargs):
  return TipsExtension(*args, **kwargs)
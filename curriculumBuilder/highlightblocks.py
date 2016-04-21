from markdown.util import etree
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import Pattern
from markdown.preprocessors import Preprocessor
import subprocess
import re

BLOCK_RE = re.compile(r'''(?:^|\n)<\ ?(?P<class>[\w\-]+)
                      (?P<title>(?:\ "(.*?)"))?>*\n(?P<content>.*?)
                      (?<=\n)?(?:^|\n)<\/ ?(?P=class)?>''',
                      re.MULTILINE | re.DOTALL | re.VERBOSE)
OPEN_RE = re.compile(r'(?:^|\n)<\ ?([\w\-]+)(?:\ "(.*?)")?>')
GUIDE_RE = re.compile(r'(?:^|\n)<guide>')
CLOSE_RE = re.compile(r'(?:^|\n)<\/ ?([\w\-]+)>')

class HighlightBlocksExtension(Extension):

  def extendMarkdown(self, md, md_globals):
    md.registerExtension(self)
    md.parser.blockprocessors.add('highlightblocks', HighlightBlocksProcessor(md.parser), '_begin')

class HighlightBlocksProcessor(BlockProcessor):

  def test(self, parent, block):
    sibling = self.lastChild(parent)
    print GUIDE_RE.search(block)
    return GUIDE_RE.search(block)

  def run(self, parent, blocks):
    print ''
    print 'running'
    print ''
    sibling = self.lastChild(parent)
    block = blocks.pop(0)
    m = GUIDE_RE.search(block)
    print m
    if m:
      block = block[m.end() + 1:]  # removes the first line
      div = etree.SubElement(parent, 'div')
      div.set('class', '%s' % "powpow")
    else:
      div = sibling


    self.parser.parseChunk(div, block)

def makeExtension(*args, **kwargs) :
  return HighlightBlocksExtension(*args, **kwargs)
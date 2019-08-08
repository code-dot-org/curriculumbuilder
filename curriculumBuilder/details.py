# pylint: disable=missing-docstring,invalid-name
"""
Python-Markdown Plugin for parsing custom detail element

See https://github.com/code-dot-org/remark-plugins/blob/master/src/details.js
for original implementation.

As of July 2019, we use detail tags extensively in CSD and CSP level
instructions to provide additional information to students. We write those in
HTML, but have implemented this syntax so we can begin writing those in pure
markdown.

Because the pullthrough exists, we also need to be able to parse that syntax
here in CurriculumBuilder. Hence, this plugin.
"""
import re
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree

OPEN_RE = r'\s*\<p\>\[(\w+)\]\<\/p\>'
CLOSE_RE = r'\s*\<p\>\[\/(\w+)\]\<\/p\>'

class DetailsExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.parser.blockprocessors.add('details',
                                      DetailsProcessor(md.parser),
                                      '_begin')

def makeExtension(*args, **kwargs):
    return DetailsExtension(*args, **kwargs)

class DetailsProcessor(BlockProcessor):
    OPEN_RE = re.compile(r'^(:{3,}) +details +\[([^\]]*)\](?: +:*)?(?:$|\n)')

    @staticmethod
    def compile_close_re(num_colons=3):
        return re.compile("(?:^|\n)(:{%d,})(?:$|\n)" % num_colons)

    def test(self, parent, block):
        return bool(self.OPEN_RE.match(block))


    def run(self, parent, blocks):
        open_block = blocks.pop(0)
        open_match = self.OPEN_RE.match(open_block)
        if open_match is None:
            return

        open_colons, summary_content = open_match.groups()

        close_match = self.compile_close_re(len(open_colons)).search(open_block, open_match.end())
        if close_match:
            inner_content = open_block[open_match.end():close_match.start()]
        else:
            inner_content = open_block[open_match.end():]
            next_block = blocks.pop(0)
            close_match = self.compile_close_re(len(open_colons)).match(next_block)
            while close_match is None and len(blocks):
                inner_content += next_block
                next_block = blocks.pop()
                close_match = self.compile_close_re(len(open_colons)).match(next_block)

        details = etree.SubElement(parent, 'details')
        summary = etree.SubElement(details, 'summary')
        self.parser.parseChunk(summary, summary_content)
        self.parser.parseChunk(details, inner_content)

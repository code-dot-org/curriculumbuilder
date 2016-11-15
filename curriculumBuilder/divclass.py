import re
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

OPEN_RE = r'\s*\<p\>\[(\w+)\]\<\/p\>'
CLOSE_RE = r'\s*\<p\>\[\/(\w+)\]\<\/p\>'


class DivClassPreprocessor(Postprocessor):
    def run(self, text):
        text = re.sub(OPEN_RE, "<div class='%s'>" % '\g<1>', text)
        text = re.sub(CLOSE_RE, "</div>", text)
        return text


class DivClassExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        self.parser = md.parser
        self.md = md
        md.postprocessors.add("divClass", DivClassPreprocessor(self), "_end")


def makeExtension(*args, **kwargs):
    return DivClassExtension(*args, **kwargs)

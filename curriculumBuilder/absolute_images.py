from __future__ import absolute_import
from __future__ import unicode_literals
from urlparse import urljoin

from markdown import Extension
from markdown.treeprocessors import Treeprocessor

BASE_URL = "//code.org/curriculum/docs/"

class AbsoluteImagesExtension(Extension):
    """ Absolute Images Extension """

    def extendMarkdown(self, md, md_globals):
        absolute_images = AbsoluteImagesTreeprocessor(md)
        absolute_images.config = self.getConfigs()
        md.treeprocessors.add("absoluteimages", absolute_images, "_end")

        md.registerExtension(self)


class AbsoluteImagesTreeprocessor(Treeprocessor):
    """ Absolute Images Treeprocessor """
    def run(self, root):
        imgs = root.getiterator("img")
        for image in imgs:
            if self.is_relative(image.attrib["src"]):
                image.set("src", self.make_external(image.attrib["src"]))

    def make_external(self, path):
        return urljoin(BASE_URL, path)

    def is_relative(self, link):
        if link.startswith('http'):
            return False
        return True


def makeExtension(configs=[]):
    """ Return an instance of the AbsoluteImagesExtension """
    return AbsoluteImagesExtension(configs=configs)
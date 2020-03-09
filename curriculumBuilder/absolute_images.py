from __future__ import absolute_import
from __future__ import unicode_literals
from urlparse import urljoin
import urllib2

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

BASE_URL = "https://code.org/curriculum/docs/"
STAGING_URL = "https://staging.code.org/curriculum/docs/"


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
        try:
            new_path = urljoin(BASE_URL, path)
            urllib2.urlopen(new_path)
            return new_path
        except:
            return urljoin(STAGING_URL, path)

    def is_relative(self, link):
        if link.startswith('http'):
            return False
        if link == '':
            return False
        return True


def makeExtension(**kwargs):
    """ Return an instance of the AbsoluteImagesExtension """
    return AbsoluteImagesExtension(**kwargs)

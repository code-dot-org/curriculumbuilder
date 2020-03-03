"""
New Tab Extension for Python-Markdown
=====================================

Modify the behavior of Links in Python-Markdown to open a in a new window. This
changes the HTML output to add target="_blank" to all generated links, except
ones which point to anchors on the existing page.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import \
    LinkPattern, ReferencePattern, AutolinkPattern, AutomailPattern, \
    LINK_RE, REFERENCE_RE, SHORT_REF_RE, AUTOLINK_RE, AUTOMAIL_RE


# pylint: disable=invalid-name, too-few-public-methods
class NewTabMixin(object):
    """Common extension logic; mixed into the existing classes."""
    def handleMatch(self, match):
        """Handles a match on a pattern; used by existing implementation."""
        elem = super(NewTabMixin, self).handleMatch(match)
        if elem is not None and not elem.get('href').startswith('#'):
            elem.set('target', '_blank')
        return elem


class NewTabLinkPattern(NewTabMixin, LinkPattern):
    """Links to URLs, e.g. [link](https://duck.co)."""
    pass


class NewTabReferencePattern(NewTabMixin, ReferencePattern):
    """Links to references, e.g. [link][1]."""
    pass


class NewTabAutolinkPattern(NewTabMixin, AutolinkPattern):
    """Autommatic links, e.g. <duck.co>."""
    pass


class NewTabAutomailPattern(NewTabMixin, AutomailPattern):
    """Autommatic links, e.g. <address@example.com>."""
    pass


class NewTabExtension(Extension):
    """Modifies HTML output to open links in a new tab."""
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['link'] = \
            NewTabLinkPattern(LINK_RE, md)
        md.inlinePatterns['reference'] = \
            NewTabReferencePattern(REFERENCE_RE, md)
        md.inlinePatterns['short_reference'] = \
            NewTabReferencePattern(SHORT_REF_RE, md)
        md.inlinePatterns['autolink'] = \
            NewTabAutolinkPattern(AUTOLINK_RE, md)
        md.inlinePatterns['automail'] = \
            NewTabAutomailPattern(AUTOMAIL_RE, md)


def makeExtension(**kwargs):
    """Loads the extension."""
    return NewTabExtension(**kwargs)

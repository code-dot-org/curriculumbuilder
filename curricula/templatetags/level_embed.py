import re
from django import template

register = template.Library()

URL_RE = '^/(?P<sub>\w+)(?P<path>.+$)'

@register.filter(name='level_embed')
def level_embed(link):
    match = re.match(URL_RE, link)
    if match is not None:
        try:
            sub = match.group('sub')
            patch = match.group('path')
            return "https://%s.code.org%s" %(sub, patch)
        except IndexError:
            logger.exception('Failed to embed page' % link)
            return link
    else:
        return link

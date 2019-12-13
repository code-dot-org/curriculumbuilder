from django import template
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
def get_absolute_url_for_host(map, host):
    if host == 'curriculum.code.org' or host == 'www.codecurricula.com' or host == 'localhost:8000' or host == 'testserver':
        return '/documentation/%s/' % map.slug
    elif host == 'studio.code.org':
        return '/docs/%s/' % map.slug
    elif host == 'docs.code.org':
        return '/%s/' % map.slug
    else:
        logger.info("no known host %s" % host)
        return '/%s/' % map.slug
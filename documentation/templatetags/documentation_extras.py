from django import template
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
def get_absolute_url_for_host(map, host):
    if host == 'www.curriculum.code.org' or host == 'wwww.codecurricula.com' or host == 'localhost:8000':
        return '/documentation/%s/' % map.slug
    elif host == 'studio.code.org':
        return '/docs/%s/' % map.slug
    elif host == 'docs.code.org':
        return '/%s/' % map.slug
    else:
        logger.info("no known host %s" % host)
        return '/%s/' % map.slug
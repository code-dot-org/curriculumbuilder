from django import template
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
def get_absolute_url_for_host(map, host):
    if host == 'testserver' or host == 'localhost:8000':
        return '/docs/%s/' % map.slug
    else:
        logger.info("no known host %s" % host)
        return '/docs/%s/' % map.slug
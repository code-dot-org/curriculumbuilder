from django import template

register = template.Library()


@register.filter
def get_absolute_url_for_host(map, host):
    if host == 'codecurricula.com' or host == 'localhost:8000':
        return '/documentation/%s/' % map.slug
    elif host == 'studio.code.org':
        return '/docs/%s/' % map.slug
    elif host == 'docs.code.org':
        return '/%s/' % map.slug
import re
from django import template

register = template.Library()

VID_RE = 'autoplay=1(&?)'

@register.filter(name='no_autoplay')
def no_autoplay(link):

    return re.sub(VID_RE, '', link)
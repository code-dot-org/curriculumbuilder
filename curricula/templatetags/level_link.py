from django import template

register = template.Library()


@register.filter(name='level_link')
def level_link(link):

    return "https://studio.code.org%s" % link[:link.find('?')]
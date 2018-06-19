from django import template

register = template.Library()


@register.filter(name='level_link')
def level_link(link):
    param_index = link.find('?')
    if param_index > -1:
        return "https://studio.code.org%s" % link[:param_index]
    else:
        return "https://studio.code.org%s" % link

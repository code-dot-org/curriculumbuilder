from django import template

register = template.Library()

@register.filter(name='with_unit')

def with_unit(value, unit):
    """
    replaces '{{{unit_name}}}' with the specified unit's name as it would
    appear in a url pointing to a script level, e.g. 'coursec-2018'.
    """
    return value.replace('{{{unit_name}}}', unit.unit_name)

from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string into a list using the given delimiter"""
    return [x.strip() for x in value.split(delimiter)] 

@register.filter
def contains(value, arg):
    """Check if a string contains another string, case-insensitive"""
    return str(arg).lower() in str(value).lower() 
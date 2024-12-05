from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Get a value from a dictionary using a key"""
    return dictionary.get(key, 0)

@register.filter
def abs_value(value):
    """Return absolute value"""
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value 
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allow dict[key] access in templates"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    try:
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary:
        return dictionary.get(key)
    return None
@register.filter
def percentage(value, arg):
    try:
        return round((float(value) / float(arg)) * 100, 1)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

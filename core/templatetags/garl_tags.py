"""
GARL Custom Template Tags and Filters
Load with: {% load garl_tags %}
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Return dictionary[key], or 0 if missing. Used in author dashboard."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return 0


@register.filter
def mul(value, arg):
    """Multiply two numbers."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """Return value as percentage of total."""
    try:
        if int(total) == 0:
            return 0
        return int((int(value) / int(total)) * 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.simple_tag
def url_replace(request, field, value):
    """Replace a single GET parameter while keeping others. Useful in pagination."""
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()

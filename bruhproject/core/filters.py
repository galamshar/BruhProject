from django import template

register = template.Library()


@register.filter
def to_str(value):
    """converts int to string"""
    return str(value)
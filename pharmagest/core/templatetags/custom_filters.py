from django import template

register = template.Library()

@register.filter
def format_ar(value):
    try:
        # On convertit en float, on formate avec des espaces, et on remplace la virgule par un espace
        return "{:,.0f}".format(float(value)).replace(",", " ")
    except (ValueError, TypeError):
        return value
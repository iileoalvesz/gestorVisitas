import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='tojson')
def to_json(value):
    """Serializa valor para JSON seguro para uso em atributos HTML/JS."""
    return mark_safe(json.dumps(value, ensure_ascii=False, default=str))


@register.filter(name='to_json')
def to_json_alias(value):
    return to_json(value)


@register.filter(name='bool_js')
def bool_js(value):
    """Converte bool Python para string JS: True → 'true', False → 'false'."""
    return 'true' if value else 'false'


@register.filter(name='is_image')
def is_image(filename):
    if not filename:
        return False
    return str(filename).lower().rsplit('.', 1)[-1] in ('jpg', 'jpeg', 'png', 'gif', 'webp')


@register.filter(name='is_pdf')
def is_pdf(filename):
    if not filename:
        return False
    return str(filename).lower().endswith('.pdf')

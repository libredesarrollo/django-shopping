from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def is_demo():
    """
    Verifica el valor de DEMO en settings y lo retorna.
    Devuelve False por defecto si no se encuentra.
    """

    return getattr(settings, 'DEMO', False)
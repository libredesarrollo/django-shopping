
from django import template
from django.template.loader import get_template, TemplateDoesNotExist

register = template.Library()

@register.simple_tag
def check_if_exists(template_name):
    try:
        get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False
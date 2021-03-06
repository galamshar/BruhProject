from crispy_forms.templatetags.crispy_forms_filters import as_crispy_form
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils.timezone import template_localtime
from jinja2 import Environment
from widget_tweaks.templatetags import widget_tweaks

from bruhproject.core import filters


def environment(**options):
    env = Environment(**options)
    env.filters.update({
        'localtime': template_localtime,
        'add_class': widget_tweaks.add_class,
        'set_attr': widget_tweaks.set_attr,
        'to_str' : filters.to_str
    })
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'localtime': template_localtime,
        'render_field': widget_tweaks.render_field,
        'crispy' : as_crispy_form
    })
    return env

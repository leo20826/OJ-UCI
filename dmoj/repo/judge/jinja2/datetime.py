import functools

from django.template.defaultfilters import date, time
from django.templatetags.tz import localtime
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.timezone import utc
from django.utils.translation import gettext as _

from . import registry


def localtime_wrapper(func):
    @functools.wraps(func)
    def wrapper(datetime, *args, **kwargs):
        if datetime and getattr(datetime, 'convert_to_local_time', True):
            datetime = localtime(datetime)
        return func(datetime, *args, **kwargs) if datetime else ""

    return wrapper


registry.filter(localtime_wrapper(date))
registry.filter(localtime_wrapper(time))


@registry.function
def relative_time(time, **kwargs):
    # Manejo robusto de valores None/empty
    if not time:
        return mark_safe('<span class="time-with-rel">—</span>')
    
    try:
        abs_time = date(time, kwargs.get('format', _('N j, Y, g:i a')))
        iso_time = time.astimezone(utc).isoformat()
        
        return mark_safe(f'<span data-iso="{iso_time}" class="time-with-rel"'
                         f' title="{escape(abs_time)}" data-format="{escape(kwargs.get("rel", _("{time}")))}">'
                         f'{escape(kwargs.get("abs", _("on {time}")).replace("{time}", abs_time))}</span>')
    except (AttributeError, ValueError):
        # Fallback si hay algún problema con el objeto datetime
        return mark_safe(f'<span class="time-with-rel">{escape(str(time))}</span>')
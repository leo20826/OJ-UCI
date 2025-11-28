"""
Django-ace originally from https://github.com/bradleyayers/django-ace.
"""

from urllib.parse import urljoin

from django import forms
from django.conf import settings
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe


class AceWidget(forms.Textarea):
    def __init__(
        self,
        mode: str | None = None,
        theme: str | None = None,
        wordwrap: bool = False,
        width: str = "100%",
        height: str = "300px",
        no_ace_media: bool = False,
        *args,
        **kwargs,
    ):
        self.mode = mode
        self.theme = theme
        self.wordwrap = wordwrap
        self.width = width
        self.height = height
        self.ace_media = not no_ace_media
        super().__init__(*args, **kwargs)

    @property
    def media(self) -> forms.Media:
        js = [urljoin(settings.ACE_URL, "ace.js")] if self.ace_media else []
        js.append("django_ace/widget.js")
        css = {
            "screen": ["django_ace/widget.css"],
        }
        return forms.Media(js=js, css=css)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}

        ace_attrs = {
            "class": "django-ace-widget loading",
            "style": f"width:{self.width}; height:{self.height}",
            "id": f"ace_{name}",
        }
        if self.mode:
            ace_attrs["data-mode"] = self.mode
        if self.theme:
            ace_attrs["data-theme"] = self.theme

        ace_attrs["data-default-light-theme"] = settings.ACE_DEFAULT_LIGHT_THEME
        ace_attrs["data-default-dark-theme"] = settings.ACE_DEFAULT_DARK_THEME

        if self.wordwrap:
            ace_attrs["data-wordwrap"] = "true"

        # Estilos predeterminados para el textarea
        attrs.update(
            style="width: 100%; min-width: 100%; max-width: 100%; resize: none"
        )
        textarea_html = super().render(name, value, attrs, renderer=renderer)

        html = f"<div{flatatt(ace_attrs)}><div></div></div>{textarea_html}"

        # Añadir toolbar
        html = (
            f'<div class="django-ace-editor">'
            f'<div style="width: 100%" class="django-ace-toolbar">'
            f'<a href="./" class="django-ace-max_min"></a>'
            f'</div>'
            f"{html}</div>"
        )

        return mark_safe(html)

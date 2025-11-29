from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import StackedInline
from django.forms import ModelForm
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from judge.models import TicketMessage
from judge.widgets import AdminHeavySelect2MultipleWidget, AdminHeavySelect2Widget, AdminMartorWidget


class TicketMessageForm(ModelForm):
    class Meta:
        widgets = {
            'user': AdminHeavySelect2Widget(data_view='profile_select2', attrs={'style': 'width: 100%'}),
            'body': AdminMartorWidget(attrs={'data-markdownfy-url': reverse_lazy('ticket_preview')}),
        }


class TicketMessageInline(StackedInline):
    model = TicketMessage
    form = TicketMessageForm
    fields = ('user', 'body')
    extra = 1  # AÑADIDO: Para permitir añadir nuevos mensajes


class TicketForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # ACTUALIZADO: super() sin argumentos
        # AÑADIDO: Deshabilitar creación de relaciones desde el widget
        if 'user' in self.fields:
            self.fields['user'].widget.can_add_related = False
        if 'assignees' in self.fields:
            self.fields['assignees'].widget.can_add_related = False

    class Meta:
        widgets = {
            'user': AdminHeavySelect2Widget(data_view='profile_select2', attrs={'style': 'width: 100%'}),
            'assignees': AdminHeavySelect2MultipleWidget(data_view='profile_select2', attrs={'style': 'width: 100%'}),
        }


class TicketAdmin(ModelAdmin):
    fields = ('title', 'time', 'user', 'assignees', 'content_type', 'object_id', 'notes')
    readonly_fields = ('time',)
    list_display = ('title', 'user', 'time', 'linked_item')
    inlines = [TicketMessageInline]
    form = TicketForm
    date_hierarchy = 'time'

    # AÑADIDO: Método linked_item para mostrar el elemento relacionado
    def linked_item(self, obj):
        if obj.linked_item:
            return format_html('<a href="{}">{}</a>', obj.linked_item.get_absolute_url(), str(obj.linked_item))
        return '-'
    linked_item.short_description = _('Linked Item')
    linked_item.admin_order_field = 'object_id'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user__user')  # ACTUALIZADO: super() sin argumentos

    # AÑADIDO: Métodos de permisos para mejor control
    def has_add_permission(self, request):
        return request.user.has_perm('judge.add_ticket')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('judge.change_ticket')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('judge.delete_ticket')
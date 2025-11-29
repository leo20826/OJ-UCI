from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class ProblemGroupAdmin(admin.ModelAdmin):
    fields = ('name', 'full_name')
    list_display = ('name', 'full_name')  # AÑADIDO: Para mostrar en lista
    search_fields = ('name', 'full_name')  # AÑADIDO: Para búsqueda
    ordering = ('name',)  # AÑADIDO: Ordenamiento por defecto

    def get_queryset(self, request):
        return super().get_queryset(request)  # ACTUALIZADO: super() sin argumentos


class ProblemTypeAdmin(admin.ModelAdmin):
    fields = ('name', 'full_name')
    list_display = ('name', 'full_name')  # AÑADIDO: Para mostrar en lista
    search_fields = ('name', 'full_name')  # AÑADIDO: Para búsqueda
    ordering = ('name',)  # AÑADIDO: Ordenamiento por defecto

    def get_queryset(self, request):
        return super().get_queryset(request)  # ACTUALIZADO: super() sin argumentos
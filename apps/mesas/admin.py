# apps/mesas/admin.py
from django.contrib import admin
from .models import Mesa

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'capacidad', 'estado')  # ✅ Eliminado 'zona'
    list_filter = ('estado',)  # ✅ Eliminado 'zona'
    list_editable = ('capacidad',)  # ✅ Eliminado 'zona'
    search_fields = ('numero',)
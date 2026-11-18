from django.contrib import admin
from .models import Fournisseur, Client

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email', 'statut')
    list_filter = ('statut',)
    search_fields = ('nom', 'telephone')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email')
    search_fields = ('nom', 'telephone')
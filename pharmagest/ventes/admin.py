from django.contrib import admin
from .models import Vente, LigneVente, RetourVente

class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 1

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date_vente', 'client', 'total', 'statut')
    list_filter = ('statut', 'date_vente')
    search_fields = ('reference',)
    inlines = [LigneVenteInline]

@admin.register(RetourVente)
class RetourVenteAdmin(admin.ModelAdmin):
    list_display = ('date_retour', 'vente_origine', 'lot', 'quantite_retournee', 'motif', 'remis_en_stock')
    list_filter = ('motif', 'remis_en_stock', 'date_retour')
    search_fields = ('vente_origine__reference', 'lot__medicament__nom_commercial')
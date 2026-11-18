from django.contrib import admin
from .models import LotStock, MouvementStock, CommandeAchat, LigneAchat, ReceptionAchat

@admin.register(LotStock)
class LotStockAdmin(admin.ModelAdmin):
    list_display = ('medicament', 'numero_lot', 'date_peremption', 'quantite_actuelle')
    list_filter = ('date_peremption', 'medicament')
    search_fields = ('numero_lot', 'medicament__nom_commercial')

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('date_mouvement', 'type_mouvement', 'lot', 'quantite', 'utilisateur')
    list_filter = ('type_mouvement', 'date_mouvement')

class LigneAchatInline(admin.TabularInline):
    model = LigneAchat
    extra = 1

@admin.register(CommandeAchat)
class CommandeAchatAdmin(admin.ModelAdmin):
    list_display = ('reference', 'fournisseur', 'statut', 'date_commande')
    list_filter = ('statut', 'date_commande')
    inlines = [LigneAchatInline]

@admin.register(ReceptionAchat)
class ReceptionAchatAdmin(admin.ModelAdmin):
    list_display = ('commande', 'numero_lot', 'quantite_recue', 'date_reception')
from django.urls import path
from . import views

app_name = 'achats_stock'

urlpatterns = [
    path('', views.liste_stock, name='stock_list'),
    path('reception/', views.ajouter_lot, name='lot_add'),
    path('stock/ajuster/', views.ajuster_stock, name='stock_ajuster'),
    path('mouvements/', views.mouvement_list, name='mouvement_list'),

    # Commandes
    path('commandes/', views.liste_commandes, name='commande_list'),
    path('commandes/ajouter/', views.ajouter_commande, name='commande_add'),
    path('commandes/<int:pk>/', views.detail_commande, name='commande_detail'),
    path('commandes/<int:pk>/valider/', views.valider_commande, name='commande_valider'),
    path('commandes/<int:pk>/annuler/', views.annuler_commande, name='commande_annuler'),
    path('lignes/<int:ligne_id>/receptionner/', views.receptionner_ligne, name='ligne_receptionner'),
    path('commandes/<int:pk>/pdf/', views.pdf_bon_commande, name='commande_pdf'),
    path('commandes/<int:pk>/pdf-reception/', views.pdf_bon_reception, name='reception_pdf'),
]
from django.urls import path
from . import views

app_name = 'ventes'

urlpatterns = [
    path('', views.liste_ventes, name='vente_list'),
    path('nouvelle/', views.nouvelle_vente, name='vente_add'),
    path('caisse/', views.caisse_rapide, name='caisse_rapide'), # <-- Nouvelle URL
    path('<int:vente_id>/recu/', views.telecharger_recu, name='telecharger_recu'),
    path('retours/', views.liste_retours, name='retour_list'),
    path('retours/ajouter/', views.ajouter_retour, name='retour_add'),
]
from django.urls import path
from . import views

app_name = 'partenaires'

urlpatterns = [
    # Fournisseurs
    path('fournisseurs/', views.liste_fournisseurs, name='fournisseur_list'),
    path('fournisseurs/ajouter/', views.ajouter_fournisseur, name='fournisseur_add'),
    path('fournisseurs/<int:pk>/modifier/', views.modifier_fournisseur, name='fournisseur_edit'),
    path('fournisseurs/<int:pk>/', views.detail_fournisseur, name='fournisseur_detail'),

    # Clients
    path('clients/', views.liste_clients, name='client_list'),
    path('clients/ajouter/', views.ajouter_client, name='client_add'),
    path('clients/<int:pk>/modifier/', views.modifier_client, name='client_edit'),
    path('clients/<int:pk>/', views.detail_client, name='client_detail'),
]
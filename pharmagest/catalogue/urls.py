from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    path('medicaments/', views.liste_medicaments, name='medicament_list'),
    path('medicaments/ajouter/', views.ajouter_medicament, name='medicament_add'),
    path('medicaments/<int:pk>/modifier/', views.modifier_medicament, name='medicament_edit'),
]
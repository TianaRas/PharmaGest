from django.urls import path
from . import views

app_name = 'rapports'

urlpatterns = [
    path('', views.index_rapports, name='index'),
    path('stock/pdf/', views.pdf_stock, name='pdf_stock'),
    path('ventes/pdf/', views.pdf_ventes, name='pdf_ventes'),
    path('achats/pdf/', views.pdf_achats, name='pdf_achats'),
    path('peremptions/pdf/', views.pdf_peremptions, name='pdf_peremptions'),
]
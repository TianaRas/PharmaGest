from django.shortcuts import render
from django.http import FileResponse
from core.decorators import rapports_requis
from achats_stock.models import LotStock, CommandeAchat
from ventes.models import Vente
from .pdf_reports import (
    generer_rapport_stock_pdf, 
    generer_rapport_ventes_pdf,
    generer_rapport_achats_pdf,
    generer_rapport_peremptions_pdf
)
from django.utils import timezone
from datetime import timedelta

@rapports_requis
def index_rapports(request):
    return render(request, 'rapports/index.html')

@rapports_requis
def pdf_stock(request):
    lots = LotStock.objects.filter(quantite_actuelle__gt=0).select_related('medicament', 'fournisseur')
    buffer = generer_rapport_stock_pdf(lots)
    return FileResponse(buffer, as_attachment=True, filename="Rapport_Stock.pdf")

@rapports_requis
def pdf_ventes(request):
    ventes = Vente.objects.filter(statut='VALIDEE').select_related('client')
    buffer = generer_rapport_ventes_pdf(ventes)
    return FileResponse(buffer, as_attachment=True, filename="Rapport_Ventes.pdf")

@rapports_requis
def pdf_achats(request):
    commandes = CommandeAchat.objects.exclude(statut='BROUILLON').select_related('fournisseur')
    buffer = generer_rapport_achats_pdf(commandes)
    return FileResponse(buffer, as_attachment=True, filename="Rapport_Achats.pdf")

@rapports_requis
def pdf_peremptions(request):
    aujourd_hui = timezone.now().date()
    dans_30_jours = aujourd_hui + timedelta(days=30)
    
    # On récupère les lots avec du stock qui périment dans moins de 30 jours
    lots = LotStock.objects.filter(
        quantite_actuelle__gt=0,
        date_peremption__lte=dans_30_jours,
        date_peremption__gte=aujourd_hui
    ).select_related('medicament').order_by('date_peremption')
    
    buffer = generer_rapport_peremptions_pdf(lots)
    return FileResponse(buffer, as_attachment=True, filename="Rapport_Peremptions.pdf")
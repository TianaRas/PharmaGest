from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import FileResponse
from django.core.paginator import Paginator
import uuid
from core.decorators import vente_requise, pharmacien_requis
from .models import Vente, LigneVente, RetourVente
from .forms import VenteForm, RetourVenteForm
from .pdf import generer_recu_pdf
from partenaires.models import Client
from achats_stock.models import LotStock, MouvementStock
from catalogue.models import Categorie


@vente_requise
def liste_ventes(request):
    tri = request.GET.get('tri', '-date_vente')
    ventes_list = Vente.objects.all().select_related('client', 'utilisateur')
    
    tris_valides = ['date_vente', '-date_vente', 'total', '-total']
    if tri in tris_valides:
        ventes_list = ventes_list.order_by(tri)
    else:
        ventes_list = ventes_list.order_by('-date_vente')
    
    paginator = Paginator(ventes_list, 10)
    page_number = request.GET.get('page')
    ventes = paginator.get_page(page_number)
    
    return render(request, 'ventes/vente_list.html', {'ventes': ventes, 'tri': tri})


@vente_requise
def nouvelle_vente(request):
    clients = Client.objects.all()
    if request.method == 'POST':
        form = VenteForm(request.POST, clients=clients)
        if form.is_valid():
            lot = form.cleaned_data['lot']
            quantite = form.cleaned_data['quantite']
            client_id = form.cleaned_data['client']
            mode_paiement = form.cleaned_data['mode_paiement']

            if lot.quantite_actuelle < quantite:
                messages.error(request, f"Stock insuffisant pour {lot.medicament.nom_commercial}. Il ne reste que {lot.quantite_actuelle} unités.")
                return redirect('ventes:vente_add')
            
            if lot.date_peremption < timezone.now().date():
                messages.error(request, f"Impossible de vendre ce lot : il est périmé depuis le {lot.date_peremption}.")
                return redirect('ventes:vente_add')

            with transaction.atomic():
                reference = f"VTE-{uuid.uuid4().hex[:6].upper()}"
                client_obj = Client.objects.get(id=client_id) if client_id else None
                
                vente = Vente.objects.create(
                    reference=reference,
                    client=client_obj,
                    utilisateur=request.user,
                    mode_paiement=mode_paiement
                )

                prix_unitaire = lot.medicament.prix_vente
                sous_total = prix_unitaire * quantite
                
                LigneVente.objects.create(
                    vente=vente,
                    lot=lot,
                    quantite=quantite,
                    prix_unitaire=prix_unitaire,
                    sous_total=sous_total
                )

                vente.total = sous_total
                vente.save()

                lot.quantite_actuelle -= quantite
                lot.save()

                MouvementStock.objects.create(
                    lot=lot,
                    type_mouvement='SORTIE',
                    quantite=-quantite,
                    motif=f"Vente {reference}",
                    utilisateur=request.user
                )

            messages.success(request, f"Vente enregistrée avec succès ! Réf: {reference}")
            return redirect('ventes:vente_list')
    else:
        form = VenteForm(clients=clients)
    
    return render(request, 'ventes/vente_form.html', {'form': form})


@vente_requise
def caisse_rapide(request):
    aujourd_hui = timezone.now().date()
    lots_disponibles = LotStock.objects.filter(
        quantite_actuelle__gt=0,
        date_peremption__gte=aujourd_hui
    ).select_related('medicament')
    
    categories = Categorie.objects.all()
    clients = Client.objects.all()

    if request.method == 'POST':
        form = VenteForm(request.POST, clients=clients)
        if form.is_valid():
            lot = form.cleaned_data['lot']
            quantite = form.cleaned_data['quantite']
            client_id = form.cleaned_data['client']
            mode_paiement = form.cleaned_data['mode_paiement']

            if lot.quantite_actuelle < quantite:
                messages.error(request, f"Stock insuffisant pour {lot.medicament.nom_commercial}. Reste: {lot.quantite_actuelle}.")
                return redirect('ventes:caisse_rapide')
            
            with transaction.atomic():
                reference = f"VTE-{uuid.uuid4().hex[:6].upper()}"
                client_obj = Client.objects.get(id=client_id) if client_id else None
                
                vente = Vente.objects.create(
                    reference=reference, client=client_obj,
                    utilisateur=request.user, mode_paiement=mode_paiement
                )

                prix_unitaire = lot.medicament.prix_vente
                sous_total = prix_unitaire * quantite
                
                LigneVente.objects.create(
                    vente=vente, lot=lot, quantite=quantite,
                    prix_unitaire=prix_unitaire, sous_total=sous_total
                )

                vente.total = sous_total
                vente.save()

                lot.quantite_actuelle -= quantite
                lot.save()

                MouvementStock.objects.create(
                    lot=lot, type_mouvement='SORTIE', quantite=-quantite,
                    motif=f"Vente {reference}", utilisateur=request.user
                )

            messages.success(request, f"Vente validée ! Réf: {reference}")
            return redirect('ventes:vente_list')
    else:
        form = VenteForm(clients=clients)

    return render(request, 'ventes/caisse.html', {
        'lots': lots_disponibles,
        'form': form,
        'categories': categories,
    })


@vente_requise
def telecharger_recu(request, vente_id):
    vente = get_object_or_404(Vente, id=vente_id)
    buffer = generer_recu_pdf(vente)
    return FileResponse(buffer, as_attachment=True, filename=f"Recu_{vente.reference}.pdf")


@pharmacien_requis
def liste_retours(request):
    retours = RetourVente.objects.all().select_related('vente_origine', 'lot__medicament', 'utilisateur')
    return render(request, 'ventes/retour_list.html', {'retours': retours})


@pharmacien_requis
def ajouter_retour(request):
    if request.method == 'POST':
        form = RetourVenteForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                retour = form.save(commit=False)
                retour.utilisateur = request.user
                retour.save()

                if retour.remis_en_stock:
                    lot = retour.lot
                    lot.quantite_actuelle += retour.quantite_retournee
                    lot.save()

                    MouvementStock.objects.create(
                        lot=lot,
                        type_mouvement='RETOUR',
                        quantite=retour.quantite_retournee,
                        motif=f"Retour sur vente {retour.vente_origine.reference}",
                        utilisateur=request.user
                    )
            messages.success(request, "Retour enregistré avec succès.")
            return redirect('ventes:retour_list')
    else:
        form = RetourVenteForm()
    
    return render(request, 'ventes/retour_form.html', {'form': form})
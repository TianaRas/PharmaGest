from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import FileResponse
from django import forms
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import uuid
from core.decorators import stock_requis
from .models import LotStock, MouvementStock, CommandeAchat, LigneAchat, ReceptionAchat
from .forms import LotStockForm, CommandeAchatForm, ReceptionAchatForm
from catalogue.models import Medicament
from rapports.pdf_achats import generer_bon_commande_pdf, generer_bon_reception_pdf

@stock_requis
def liste_stock(request):
    tri = request.GET.get('tri', 'date_peremption')
    lots_list = LotStock.objects.filter(quantite_actuelle__gt=0).select_related('medicament', 'fournisseur')
    
    if tri in ['date_peremption', '-date_peremption', 'quantite_actuelle', '-quantite_actuelle']:
        lots_list = lots_list.order_by(tri)
    else:
        lots_list = lots_list.order_by('date_peremption')
        
    paginator = Paginator(lots_list, 10)
    page_number = request.GET.get('page')
    lots = paginator.get_page(page_number)
    
    # --- CALCUL DES BADGES DE PÉREMPTION ---
    aujourd_hui = timezone.now().date()
    for lot in lots:
        jours_restants = (lot.date_peremption - aujourd_hui).days
        
        if jours_restants < 0:
            lot.peremption_statut = 'PERIME'
            lot.peremption_couleur = 'danger'
            lot.peremption_texte = 'Périmé'
        elif jours_restants <= 30:
            lot.peremption_statut = 'CRITIQUE'
            lot.peremption_couleur = 'warning'
            lot.peremption_texte = f'Expire dans {jours_restants} j'
        elif jours_restants <= 90:
            lot.peremption_statut = 'ATTENTION'
            lot.peremption_couleur = 'info'
            lot.peremption_texte = f'Expire dans {jours_restants} j'
        else:
            lot.peremption_statut = 'VALIDE'
            lot.peremption_couleur = 'success'
            lot.peremption_texte = 'Valide'

    return render(request, 'achats_stock/stock_list.html', {'lots': lots, 'tri': tri})

@stock_requis
def ajouter_lot(request):
    if request.method == 'POST':
        form = LotStockForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                lot = form.save()
                MouvementStock.objects.create(
                    lot=lot, type_mouvement='ENTREE', quantite=lot.quantite_actuelle,
                    motif="Réception initiale", utilisateur=request.user
                )
            messages.success(request, f"Lot {lot.numero_lot} ajouté au stock.")
            return redirect('achats_stock:stock_list')
    else:
        form = LotStockForm()
    return render(request, 'achats_stock/lot_form.html', {'form': form, 'titre': 'Enregistrer une réception de stock'})

@stock_requis
def liste_commandes(request):
    tri = request.GET.get('tri', '-date_commande')
    commandes_list = CommandeAchat.objects.all().select_related('fournisseur')
    
    if tri in ['date_commande', '-date_commande', 'statut', '-statut']:
        commandes_list = commandes_list.order_by(tri)
    else:
        commandes_list = commandes_list.order_by('-date_commande')
        
    return render(request, 'achats_stock/commande_list.html', {'commandes': commandes_list, 'tri': tri})

@stock_requis
def ajouter_commande(request):
    if request.method == 'POST':
        form = CommandeAchatForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.utilisateur = request.user
            if not commande.reference:
                commande.reference = f"CMD-{uuid.uuid4().hex[:6].upper()}"
            commande.save()
            messages.success(request, "Commande créée. Ajoutez maintenant des médicaments.")
            return redirect('achats_stock:commande_detail', pk=commande.pk)
    else:
        form = CommandeAchatForm()
    return render(request, 'achats_stock/commande_form.html', {'form': form, 'titre': 'Nouvelle commande'})

@stock_requis
def detail_commande(request, pk):
    commande = get_object_or_404(CommandeAchat, pk=pk)
    
    if request.method == 'POST':
        medicament_id = request.POST.get('medicament')
        quantite = request.POST.get('quantite')
        prix = request.POST.get('prix')
        
        if medicament_id and quantite and prix:
            medicament = get_object_or_404(Medicament, id=medicament_id)
            LigneAchat.objects.create(
                commande=commande, medicament=medicament,
                quantite_commandee=quantite, prix_achat_unitaire=prix
            )
            messages.success(request, "Médicament ajouté à la commande.")
            return redirect('achats_stock:commande_detail', pk=commande.pk)

    medicaments = Medicament.objects.filter(statut='ACTIF')
    return render(request, 'achats_stock/commande_detail.html', {
        'commande': commande, 'medicaments': medicaments
    })

@stock_requis
def valider_commande(request, pk):
    commande = get_object_or_404(CommandeAchat, pk=pk)
    if commande.statut == 'BROUILLON':
        commande.statut = 'COMMANDEE'
        commande.save()
        messages.success(request, "Commande validée. En attente de réception.")
    return redirect('achats_stock:commande_detail', pk=commande.pk)

@stock_requis
def annuler_commande(request, pk):
    commande = get_object_or_404(CommandeAchat, pk=pk)
    if commande.statut in ['BROUILLON', 'COMMANDEE', 'PARTIELLE']:
        commande.statut = 'ANNULEE'
        commande.save()
        messages.warning(request, "Commande annulée.")
    return redirect('achats_stock:commande_detail', pk=commande.pk)

@stock_requis
def receptionner_ligne(request, ligne_id):
    ligne = get_object_or_404(LigneAchat, pk=ligne_id)
    commande = ligne.commande
    
    if commande.statut not in ['COMMANDEE', 'PARTIELLE']:
        messages.error(request, "Cette commande n'est pas en attente de réception.")
        return redirect('achats_stock:commande_detail', pk=commande.pk)

    if request.method == 'POST':
        form = ReceptionAchatForm(request.POST)
        if form.is_valid():
            quantite = form.cleaned_data['quantite_recue']
            if quantite > ligne.reste_a_recevoir:
                messages.error(request, f"Impossible de recevoir plus de {ligne.reste_a_recevoir} unités.")
                return redirect('achats_stock:commande_detail', pk=commande.pk)

            with transaction.atomic():
                reception = form.save(commit=False)
                reception.commande = commande
                reception.utilisateur = request.user
                reception.save()

                lot = LotStock.objects.create(
                    medicament=ligne.medicament,
                    numero_lot=reception.numero_lot,
                    date_peremption=reception.date_peremption,
                    quantite_actuelle=quantite,
                    fournisseur=commande.fournisseur
                )
                MouvementStock.objects.create(
                    lot=lot, type_mouvement='ENTREE', quantite=quantite,
                    motif=f"Réception partielle commande {commande.reference}", utilisateur=request.user
                )

                ligne.quantite_recue += quantite
                ligne.save()

                if all(l.reste_a_recevoir == 0 for l in commande.lignes.all()):
                    commande.statut = 'RECEPTIONNEE'
                else:
                    commande.statut = 'PARTIELLE'
                commande.save()

            messages.success(request, f"{quantite} unités reçues pour {ligne.medicament.nom_commercial}.")
            return redirect('achats_stock:commande_detail', pk=commande.pk)
    else:
        form = ReceptionAchatForm()

    return render(request, 'achats_stock/reception_ligne_form.html', {'form': form, 'ligne': ligne})

@stock_requis
def pdf_bon_commande(request, pk):
    commande = get_object_or_404(CommandeAchat, pk=pk)
    buffer = generer_bon_commande_pdf(commande)
    return FileResponse(buffer, as_attachment=True, filename=f"Bon_Commande_{commande.reference}.pdf")

@stock_requis
def pdf_bon_reception(request, pk):
    commande = get_object_or_404(CommandeAchat, pk=pk)
    buffer = generer_bon_reception_pdf(commande)
    return FileResponse(buffer, as_attachment=True, filename=f"Bon_Reception_{commande.reference}.pdf")

class AjustementStockForm(forms.Form):
    lot = forms.ModelChoiceField(
        queryset=LotStock.objects.filter(quantite_actuelle__gt=0),
        label="Lot à ajuster",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    nouvelle_quantite = forms.IntegerField(
        min_value=0,
        label="Nouvelle quantité réelle (après comptage)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    motif = forms.CharField(
        max_length=200,
        label="Motif de l'ajustement (ex: Casse, Perte, Inventaire)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

@stock_requis
def ajuster_stock(request):
    if request.method == 'POST':
        form = AjustementStockForm(request.POST)
        if form.is_valid():
            lot = form.cleaned_data['lot']
            nouvelle_quantite = form.cleaned_data['nouvelle_quantite']
            motif = form.cleaned_data['motif']

            difference = nouvelle_quantite - lot.quantite_actuelle

            if difference == 0:
                messages.info(request, "La quantité est identique, aucun ajustement nécessaire.")
                return redirect('achats_stock:stock_list')

            with transaction.atomic():
                lot.quantite_actuelle = nouvelle_quantite
                lot.save()
                MouvementStock.objects.create(
                    lot=lot,
                    type_mouvement='AJUSTEMENT',
                    quantite=difference,
                    motif=motif,
                    utilisateur=request.user
                )

            messages.success(request, f"Ajustement enregistré : {difference} unités pour le lot {lot.numero_lot}.")
            return redirect('achats_stock:stock_list')
    else:
        form = AjustementStockForm()

    return render(request, 'achats_stock/ajustement_form.html', {'form': form})

@stock_requis
def mouvement_list(request):
    mouvements_list = MouvementStock.objects.all().select_related('lot__medicament', 'utilisateur').order_by('-date_mouvement')
    paginator = Paginator(mouvements_list, 20)
    page_number = request.GET.get('page')
    mouvements = paginator.get_page(page_number)
    return render(request, 'achats_stock/mouvement_list.html', {'mouvements': mouvements})
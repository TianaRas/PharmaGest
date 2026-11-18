from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.decorators import pharmacien_requis, vente_requise
from .models import Fournisseur, Client
from .forms import FournisseurForm, ClientForm
from ventes.models import Vente

# --- FOURNISSEURS ---
@pharmacien_requis
def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'partenaires/fournisseur_list.html', {'fournisseurs': fournisseurs})

@pharmacien_requis
def ajouter_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur ajouté avec succès.")
            return redirect('partenaires:fournisseur_list')
    else:
        form = FournisseurForm()
    return render(request, 'partenaires/fournisseur_form.html', {'form': form, 'titre': 'Ajouter un fournisseur'})

@pharmacien_requis
def modifier_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur modifié avec succès.")
            return redirect('partenaires:fournisseur_list')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'partenaires/fournisseur_form.html', {'form': form, 'titre': 'Modifier un fournisseur'})

@pharmacien_requis
def detail_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    from achats_stock.models import CommandeAchat
    commandes = CommandeAchat.objects.filter(fournisseur=fournisseur).order_by('-date_commande')
    return render(request, 'partenaires/fournisseur_detail.html', {
        'fournisseur': fournisseur,
        'commandes': commandes
    })

# --- CLIENTS ---
@vente_requise
def liste_clients(request):
    clients = Client.objects.all()
    return render(request, 'partenaires/client_list.html', {'clients': clients})

@vente_requise
def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client ajouté avec succès.")
            return redirect('partenaires:client_list')
    else:
        form = ClientForm()
    return render(request, 'partenaires/client_form.html', {'form': form, 'titre': 'Ajouter un client'})

@vente_requise
def modifier_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client modifié avec succès.")
            return redirect('partenaires:client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'partenaires/client_form.html', {'form': form, 'titre': 'Modifier un client'})

@vente_requise
def detail_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    ventes = Vente.objects.filter(client=client).order_by('-date_vente')
    return render(request, 'partenaires/client_detail.html', {
        'client': client,
        'ventes': ventes
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from core.decorators import pharmacien_requis
from .models import Medicament, Categorie
from .forms import MedicamentForm
from django.core.paginator import Paginator 
from django.core.paginator import Paginator

@pharmacien_requis
def liste_medicaments(request):
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie', '')
    tri = request.GET.get('tri', 'nom_commercial')  # Tri par défaut
    
    medicaments_list = Medicament.objects.filter(statut='ACTIF').select_related('categorie')
    
    if query:
        medicaments_list = medicaments_list.filter(
            Q(nom_commercial__icontains=query) | 
            Q(code_barres__icontains=query)
        )
    
    if categorie_id:
        medicaments_list = medicaments_list.filter(categorie_id=categorie_id)
    
    # Application du tri
    tris_valides = ['nom_commercial', '-nom_commercial', 'prix_vente', '-prix_vente', 'date_creation', '-date_creation']
    if tri in tris_valides:
        medicaments_list = medicaments_list.order_by(tri)
    else:
        medicaments_list = medicaments_list.order_by('nom_commercial')
    
    paginator = Paginator(medicaments_list, 10)
    page_number = request.GET.get('page')
    medicaments = paginator.get_page(page_number)
        
    categories = Categorie.objects.all()
    
    return render(request, 'catalogue/medicament_list.html', {
        'medicaments': medicaments,
        'categories': categories,
        'query': query,
        'categorie_selectionnee': categorie_id,
        'tri': tri,
    })

@pharmacien_requis
def ajouter_medicament(request):
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Le médicament a été ajouté avec succès.")
            return redirect('catalogue:medicament_list')
    else:
        form = MedicamentForm()
    
    return render(request, 'catalogue/medicament_form.html', {'form': form, 'titre': 'Ajouter un médicament'})

@pharmacien_requis
def modifier_medicament(request, pk):
    medicament = get_object_or_404(Medicament, pk=pk)
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES, instance=medicament)
        if form.is_valid():
            form.save()
            messages.success(request, "Le médicament a été modifié avec succès.")
            return redirect('catalogue:medicament_list')
    else:
        form = MedicamentForm(instance=medicament)
    
    return render(request, 'catalogue/medicament_form.html', {'form': form, 'titre': 'Modifier un médicament'})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, F
from django.db import models
from datetime import timedelta, datetime
import json

from catalogue.models import Medicament, Categorie
from ventes.models import Vente, LigneVente
from achats_stock.models import LotStock, CommandeAchat
from utilisateurs.models import JournalAudit
from core.decorators import admin_requis

@login_required
def dashboard(request):
    aujourd_hui = timezone.now().date()
    dans_30_jours = aujourd_hui + timedelta(days=30)

    # --- GESTION DE LA PÉRIODE ---
    date_debut_str = request.GET.get('date_debut')
    date_fin_str = request.GET.get('date_fin')

    if date_debut_str and date_fin_str:
        try:
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            date_debut = aujourd_hui - timedelta(days=30)
            date_fin = aujourd_hui
    else:
        date_debut = aujourd_hui - timedelta(days=30)
        date_fin = aujourd_hui

    # 1. Statistiques générales (du jour)
    nb_medicaments = Medicament.objects.filter(statut='ACTIF').count()
    ventes_du_jour = Vente.objects.filter(date_vente__date=aujourd_hui, statut='VALIDEE').aggregate(total=Sum('total'))['total'] or 0

    # 2. Alertes de stock
    lots_stock_faible = LotStock.objects.filter(
        quantite_actuelle__gt=0,
        quantite_actuelle__lte=F('medicament__seuil_alerte')
    ).select_related('medicament')

    # 3. Péremptions proches
    lots_peremption_proche = LotStock.objects.filter(
        quantite_actuelle__gt=0,
        date_peremption__lte=dans_30_jours,
        date_peremption__gte=aujourd_hui
    ).select_related('medicament')

    # 4. Statistiques sur la période filtrée
    ventes_periode = Vente.objects.filter(
        date_vente__date__gte=date_debut, 
        date_vente__date__lte=date_fin,
        statut='VALIDEE'
    )
    total_ventes_periode = ventes_periode.aggregate(total=Sum('total'))['total'] or 0
    
    achats_periode = CommandeAchat.objects.filter(
        date_commande__date__gte=date_debut,
        date_commande__date__lte=date_fin,
        statut__in=['COMMANDEE', 'PARTIELLE', 'RECEPTIONNEE'] 
    ).aggregate(total=Sum('lignes__prix_achat_unitaire'))['total'] or 0

    # 5. Top 5 des produits les plus vendus
    top_produits = LigneVente.objects.filter(
        vente__date_vente__date__gte=date_debut,
        vente__date_vente__date__lte=date_fin,
        vente__statut='VALIDEE'
    ).values('lot__medicament__nom_commercial').annotate(
        total_vendu=Sum('quantite')
    ).order_by('-total_vendu')[:5]

    # 6. Graphique des 7 derniers jours (Ventes ET Achats)
    ventes_7_jours = []
    achats_7_jours = []
    labels_7_jours = []
    for i in range(6, -1, -1):
        jour = aujourd_hui - timedelta(days=i)
        total_vente = Vente.objects.filter(date_vente__date=jour, statut='VALIDEE').aggregate(total=Sum('total'))['total'] or 0
        ventes_7_jours.append(float(total_vente))
        
        total_achat = CommandeAchat.objects.filter(
            date_commande__date=jour, 
            statut__in=['COMMANDEE', 'PARTIELLE', 'RECEPTIONNEE']
        ).aggregate(total=Sum('lignes__prix_achat_unitaire'))['total'] or 0
        achats_7_jours.append(float(total_achat))
        
        labels_7_jours.append(jour.strftime('%d/%m'))

    # 7. Les 5 dernières ventes
    dernieres_ventes = Vente.objects.filter(statut='VALIDEE').order_by('-date_vente')[:5]

    # 8. Calcul des ventes par catégorie (pour le camembert)
    toutes_les_categories = Categorie.objects.all()
    
    # On calcule la quantité totale vendue par catégorie sur la période
    ventes_par_categorie = LigneVente.objects.filter(
        vente__date_vente__date__gte=date_debut,
        vente__date_vente__date__lte=date_fin,
        vente__statut='VALIDEE'
    ).values('lot__medicament__categorie__id').annotate(
        total_articles=Sum('quantite')
    )

    # Dictionnaire de correspondance {categorie_id: quantite_vendue}
    dict_ventes = {item['lot__medicament__categorie__id']: item['total_articles'] for item in ventes_par_categorie}

    cat_labels = []
    cat_data = []
    cat_colors = []
    cat_percentages = []
    
    palette = ['#10b981', '#f59e0b', '#8b5cf6', '#3b82f6', '#ef4444', '#06b6d4', '#6366f1']
    
    total_articles_vendus = sum(dict_ventes.values()) if dict_ventes else 1

    # On boucle sur TOUTES les catégories pour être sûr qu'elles apparaissent
    for index, cat in enumerate(toutes_les_categories):
        nom_cat = cat.nom
        qte = dict_ventes.get(cat.id, 0) # Si 0 vente, on met 0
        
        cat_labels.append(nom_cat)
        cat_data.append(qte)
        
        pct = round((qte / total_articles_vendus) * 100, 1) if total_articles_vendus > 0 else 0
        cat_percentages.append(f"{pct}%")
        
        cat_colors.append(palette[index % len(palette)])

    context = {
        'nb_medicaments': nb_medicaments,
        'ca_jour': ventes_du_jour,
        'lots_stock_faible': lots_stock_faible,
        'lots_peremption_proche': lots_peremption_proche,
        'dernieres_ventes': dernieres_ventes,
        
        'date_debut': date_debut.strftime('%Y-%m-%d'),
        'date_fin': date_fin.strftime('%Y-%m-%d'),
        'total_ventes_periode': total_ventes_periode,
        'total_achats_periode': achats_periode,
        'top_produits': top_produits,
        
        'ventes_7_jours': json.dumps(ventes_7_jours),
        'achats_7_jours': json.dumps(achats_7_jours),
        'labels_7_jours': json.dumps(labels_7_jours),
        
        'cat_labels': json.dumps(cat_labels),
        'cat_data': json.dumps(cat_data),
        'cat_colors': json.dumps(cat_colors),
        'cat_percentages': json.dumps(cat_percentages),
    }

    return render(request, 'core/dashboard.html', context)


@admin_requis
def journal_audit(request):
    logs = JournalAudit.objects.all().select_related('utilisateur')[:200]
    return render(request, 'core/journal_audit.html', {'logs': logs})
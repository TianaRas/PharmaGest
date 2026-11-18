from django.db import models
from catalogue.models import Medicament
from partenaires.models import Client
from achats_stock.models import LotStock
from utilisateurs.models import Utilisateur

class Vente(models.Model):
    STATUT_CHOICES = [
        ('VALIDEE', 'Validée'),
        ('ANNULEE', 'Annulée'),
    ]
    MODE_PAIEMENT_CHOICES = [
        ('ESPECES', 'Espèces'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('AUTRE', 'Autre'),
    ]

    reference = models.CharField(max_length=50, unique=True, verbose_name="Référence")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Client")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, verbose_name="Vendu par")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total (Ar)")
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='ESPECES', verbose_name="Mode de paiement")
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='VALIDEE', verbose_name="Statut")
    date_vente = models.DateTimeField(auto_now_add=True, verbose_name="Date de vente")

    class Meta:
        ordering = ['-date_vente']
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"

    def __str__(self):
        return f"Vente {self.reference} - {self.total} Ar"

class LigneVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes', verbose_name="Vente")
    lot = models.ForeignKey(LotStock, on_delete=models.PROTECT, verbose_name="Lot vendu")
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire (Ar)")
    sous_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sous-total (Ar)")

    def __str__(self):
        return f"{self.lot.medicament.nom_commercial} x {self.quantite}"


class RetourVente(models.Model):
    MOTIF_CHOICES = [
        ('ERREUR', 'Erreur de délivrance'),
        ('CASSE', 'Produit cassé / endommagé'),
        ('ALLERGIE', 'Allergie / Effet indésirable'),
        ('AUTRE', 'Autre motif'),
    ]

    vente_origine = models.ForeignKey(Vente, on_delete=models.PROTECT, related_name='retours', verbose_name="Vente d'origine")
    lot = models.ForeignKey(LotStock, on_delete=models.PROTECT, verbose_name="Lot retourné")
    quantite_retournee = models.PositiveIntegerField(verbose_name="Quantité retournée")
    motif = models.CharField(max_length=20, choices=MOTIF_CHOICES, verbose_name="Motif du retour")
    commentaire = models.TextField(blank=True, verbose_name="Commentaire / Détails")
    remis_en_stock = models.BooleanField(default=False, verbose_name="Remis en stock ?")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, verbose_name="Traité par")
    date_retour = models.DateTimeField(auto_now_add=True, verbose_name="Date du retour")

    class Meta:
        ordering = ['-date_retour']
        verbose_name = "Retour de vente"
        verbose_name_plural = "Retours de vente"

    def __str__(self):
        return f"Retour {self.vente_origine.reference} - {self.quantite_retournee}x {self.lot.medicament.nom_commercial}"
from django.db import models
from catalogue.models import Medicament
from partenaires.models import Fournisseur
from utilisateurs.models import Utilisateur

class LotStock(models.Model):
    medicament = models.ForeignKey(Medicament, on_delete=models.PROTECT, related_name='lots', verbose_name="Médicament")
    numero_lot = models.CharField(max_length=50, verbose_name="Numéro de lot")
    date_peremption = models.DateField(verbose_name="Date de péremption")
    quantite_actuelle = models.PositiveIntegerField(default=0, verbose_name="Quantité en stock")
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fournisseur")
    date_reception = models.DateTimeField(auto_now_add=True, verbose_name="Date de réception")

    class Meta:
        ordering = ['date_peremption']
        verbose_name = "Lot de stock"
        verbose_name_plural = "Lots de stock"

    def __str__(self):
        return f"{self.medicament.nom_commercial} - Lot {self.numero_lot} (Exp: {self.date_peremption})"


class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée (Réception)'),
        ('SORTIE', 'Sortie (Vente)'),
        ('AJUSTEMENT', 'Ajustement / Inventaire'),
        ('RETOUR', 'Retour Client'),
    ]

    lot = models.ForeignKey(LotStock, on_delete=models.PROTECT, related_name='mouvements', verbose_name="Lot concerné")
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type de mouvement")
    quantite = models.IntegerField(verbose_name="Quantité (+ ou -)")
    motif = models.CharField(max_length=200, blank=True, verbose_name="Motif / Référence")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, verbose_name="Utilisateur")
    date_mouvement = models.DateTimeField(auto_now_add=True, verbose_name="Date du mouvement")

    class Meta:
        ordering = ['-date_mouvement']
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"

    def __str__(self):
        return f"{self.get_type_mouvement_display()} - {self.lot.medicament.nom_commercial} ({self.quantite})"


class CommandeAchat(models.Model):
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('COMMANDEE', 'Commandée'),
        ('PARTIELLE', 'Partiellement réceptionnée'), # <-- AJOUT
        ('RECEPTIONNEE', 'Entièrement réceptionnée'),
        ('ANNULEE', 'Annulée'),                      # <-- AJOUT
    ]

    reference = models.CharField(max_length=50, unique=True, verbose_name="Référence")
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT, verbose_name="Fournisseur")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='BROUILLON', verbose_name="Statut")
    date_commande = models.DateTimeField(auto_now_add=True, verbose_name="Date de la commande")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")

    class Meta:
        ordering = ['-date_commande']
        verbose_name = "Commande d'achat"
        verbose_name_plural = "Commandes d'achat"

    @property
    def total_commande(self):
        return sum(ligne.sous_total for ligne in self.lignes.all())

    def __str__(self):
        return f"{self.reference} - {self.fournisseur.nom}"


class LigneAchat(models.Model):
    commande = models.ForeignKey(CommandeAchat, on_delete=models.CASCADE, related_name='lignes', verbose_name="Commande")
    medicament = models.ForeignKey(Medicament, on_delete=models.PROTECT, verbose_name="Médicament")
    quantite_commandee = models.PositiveIntegerField(verbose_name="Quantité commandée")
    prix_achat_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix d'achat unitaire")
    quantite_recue = models.PositiveIntegerField(default=0, verbose_name="Quantité reçue") # <-- AJOUT POUR PARTIEL

    @property
    def sous_total(self):
        return self.quantite_commandee * self.prix_achat_unitaire
    
    @property
    def reste_a_recevoir(self):
        return self.quantite_commandee - self.quantite_recue

    def __str__(self):
        return f"{self.medicament.nom_commercial} x {self.quantite_commandee}"


class ReceptionAchat(models.Model):
    commande = models.ForeignKey(CommandeAchat, on_delete=models.PROTECT, related_name='receptions', verbose_name="Commande")
    numero_lot = models.CharField(max_length=50, verbose_name="Numéro de lot reçu")
    date_peremption = models.DateField(verbose_name="Date de péremption")
    quantite_recue = models.PositiveIntegerField(verbose_name="Quantité effectivement reçue")
    date_reception = models.DateTimeField(auto_now_add=True, verbose_name="Date de réception")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, verbose_name="Réceptionné par")

    def __str__(self):
        return f"Réception {self.commande.reference} - {self.numero_lot}"
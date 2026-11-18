from django.db import models

class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nom']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom


class Medicament(models.Model):
    # Choix pour la forme
    FORME_CHOICES = [
        ('COMPRIME', 'Comprimé'),
        ('SIROP', 'Sirop'),
        ('GELULE', 'Gélule'),
        ('INJECTION', 'Injection'),
        ('POMMADE', 'Pommade'),
        ('AUTRE', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('ARCHIVE', 'Archivé'),
    ]

    nom_commercial = models.CharField(max_length=200, verbose_name="Nom commercial")
    denomination_generique = models.CharField(max_length=200, blank=True, verbose_name="Dénomination générique (DCI)")
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name='medicaments', verbose_name="Catégorie")
    forme = models.CharField(max_length=20, choices=FORME_CHOICES, default='COMPRIME', verbose_name="Forme")
    dosage = models.CharField(max_length=50, blank=True, verbose_name="Dosage (ex: 500mg)")
    laboratoire = models.CharField(max_length=200, blank=True, verbose_name="Laboratoire")
    code_barres = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Code-barres")
    photo = models.ImageField(upload_to='medicaments/', blank=True, null=True, verbose_name="Photo")
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix d'achat (Ar)")
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de vente (Ar)")
    seuil_alerte = models.PositiveIntegerField(default=10, verbose_name="Seuil d'alerte")
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='ACTIF', verbose_name="Statut")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nom_commercial']
        verbose_name = "Médicament"
        verbose_name_plural = "Médicaments"

    def __str__(self):
        return f"{self.nom_commercial} ({self.dosage})" if self.dosage else self.nom_commercial
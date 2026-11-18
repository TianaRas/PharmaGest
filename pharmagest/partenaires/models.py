from django.db import models

class Fournisseur(models.Model):
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
    ]

    nom = models.CharField(max_length=200, verbose_name="Nom ou raison sociale")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Adresse e-mail")
    numero_fiscal = models.CharField(max_length=50, blank=True, verbose_name="Numéro fiscal")
    contact_principal = models.CharField(max_length=100, blank=True, verbose_name="Contact principal")
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='ACTIF', verbose_name="Statut")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nom']
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"

    def __str__(self):
        return self.nom


class Client(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom du client")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Adresse e-mail")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nom']
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.nom
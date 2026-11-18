from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrateur'
    PHARMACIEN = 'PHARMACIEN', 'Pharmacien responsable'
    GESTIONNAIRE_STOCK = 'GESTIONNAIRE_STOCK', 'Gestionnaire de stock'
    CAISSIER = 'CAISSIER', 'Caissier'
    RESPONSABLE_GESTION = 'RESPONSABLE_GESTION', 'Responsable de gestion'


class Utilisateur(AbstractUser):
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.CAISSIER,
        verbose_name="Rôle",
    )
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    actif = models.BooleanField(default=True, verbose_name="Compte actif")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def est_admin(self):
        return self.role == Role.ADMIN or self.is_superuser

    def peut_vendre(self):
        return self.role in (Role.ADMIN, Role.CAISSIER, Role.PHARMACIEN)

    def peut_gerer_stock(self):
        return self.role in (Role.ADMIN, Role.GESTIONNAIRE_STOCK, Role.PHARMACIEN)

    def peut_voir_rapports(self):
        return self.role in (Role.ADMIN, Role.RESPONSABLE_GESTION, Role.PHARMACIEN)


class JournalAudit(models.Model):
    utilisateur = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL, null=True,
        verbose_name="Utilisateur"
    )
    action = models.CharField(max_length=200, verbose_name="Action")
    objet = models.CharField(max_length=200, blank=True, verbose_name="Objet concerné")
    details = models.TextField(blank=True, verbose_name="Détails")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    class Meta:
        ordering = ['-date']
        verbose_name = "Entrée du journal d'audit"
        verbose_name_plural = "Journal d'audit"

    def __str__(self):
        return f"{self.date:%d/%m/%Y %H:%M} - {self.utilisateur} - {self.action}"
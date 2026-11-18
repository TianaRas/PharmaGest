from django.db.models.signals import post_save
from django.dispatch import receiver
from utilisateurs.models import JournalAudit
from .models import Vente

@receiver(post_save, sender=Vente)
def tracer_vente(sender, instance, created, **kwargs):
    if created:
        # On trace la création d'une vente
        JournalAudit.objects.create(
            utilisateur=instance.utilisateur,
            action="Vente enregistrée",
            objet=f"Vente {instance.reference}",
            details=f"Montant: {instance.total} Ar | Paiement: {instance.get_mode_paiement_display()}"
        )
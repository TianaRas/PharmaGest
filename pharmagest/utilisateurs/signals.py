from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import JournalAudit


@receiver(user_logged_in)
def log_connexion(sender, request, user, **kwargs):
    JournalAudit.objects.create(
        utilisateur=user,
        action="Connexion",
        details=f"Connexion depuis {request.META.get('REMOTE_ADDR', '?')}",
    )
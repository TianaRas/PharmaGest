from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Utilisateur, JournalAudit


@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'role', 'actif', 'is_staff')
    list_filter = ('role', 'actif', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations PharmaGest', {'fields': ('role', 'telephone', 'actif')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations PharmaGest', {'fields': ('role', 'telephone', 'actif')}),
    )


@admin.register(JournalAudit)
class JournalAuditAdmin(admin.ModelAdmin):
    list_display = ('date', 'utilisateur', 'action', 'objet')
    list_filter = ('date', 'utilisateur')
    search_fields = ('action', 'objet', 'details')
    readonly_fields = ('date',)
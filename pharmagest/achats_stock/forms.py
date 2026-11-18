from django import forms
from .models import LotStock, CommandeAchat, ReceptionAchat, LigneAchat

class LotStockForm(forms.ModelForm):
    class Meta:
        model = LotStock
        fields = ['medicament', 'numero_lot', 'date_peremption', 'quantite_actuelle', 'fournisseur']
        widgets = {
            'medicament': forms.Select(attrs={'class': 'form-select'}),
            'numero_lot': forms.TextInput(attrs={'class': 'form-control'}),
            'date_peremption': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantite_actuelle': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
        }

class CommandeAchatForm(forms.ModelForm):
    class Meta:
        model = CommandeAchat
        fields = ['fournisseur', 'reference']
        widgets = {
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: CMD-2026-001 (Laissez vide pour auto)'}),
        }

class ReceptionAchatForm(forms.ModelForm):
    class Meta:
        model = ReceptionAchat
        fields = ['numero_lot', 'date_peremption', 'quantite_recue']
        widgets = {
            'numero_lot': forms.TextInput(attrs={'class': 'form-control'}),
            'date_peremption': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantite_recue': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
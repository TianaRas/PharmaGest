from django import forms
from .models import Medicament, Categorie
import os

class MedicamentForm(forms.ModelForm):
    class Meta:
        model = Medicament
        fields = [
            'nom_commercial', 'denomination_generique', 'categorie', 
            'forme', 'dosage', 'laboratoire', 'code_barres', 
            'photo', 'prix_achat', 'prix_vente', 'seuil_alerte', 'statut'
        ]
        widgets = {
            'nom_commercial': forms.TextInput(attrs={'class': 'form-control'}),
            'denomination_generique': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'forme': forms.Select(attrs={'class': 'form-select'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'laboratoire': forms.TextInput(attrs={'class': 'form-control'}),
            'code_barres': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix_vente': forms.NumberInput(attrs={'class': 'form-control'}),
            'seuil_alerte': forms.NumberInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # 1. Vérification du poids (max 2 Mo)
            if photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError("L'image est trop lourde. La taille maximale est de 2 Mo.")
            
            # 2. Vérification de l'extension
            ext = os.path.splitext(photo.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                raise forms.ValidationError("Format d'image non supporté. Utilisez JPG ou PNG.")
                
        return photo
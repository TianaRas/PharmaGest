from django import forms
from .models import Vente
from achats_stock.models import LotStock
from .models import Vente, RetourVente # Ajoute RetourVente à l'import

class VenteForm(forms.Form):
    # On permet de choisir un lot spécifique (qui affichera le nom du médicament et le n° de lot)
    lot = forms.ModelChoiceField(
        queryset=LotStock.objects.filter(quantite_actuelle__gt=0),
        label="Médicament / Lot",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantite = forms.IntegerField(
        min_value=1, 
        label="Quantité", 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    client = forms.ChoiceField(
        required=False, 
        label="Client (optionnel)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    mode_paiement = forms.ChoiceField(
        choices=Vente.MODE_PAIEMENT_CHOICES, 
        label="Mode de paiement",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        clients = kwargs.pop('clients', None)
        super().__init__(*args, **kwargs)
        if clients is not None:
            self.fields['client'].choices = [('', '--- Client comptoir (Anonyme) ---')] + [(c.id, c.nom) for c in clients]



class RetourVenteForm(forms.ModelForm):
    class Meta:
        model = RetourVente
        fields = ['vente_origine', 'lot', 'quantite_retournee', 'motif', 'commentaire', 'remis_en_stock']
        widgets = {
            'vente_origine': forms.Select(attrs={'class': 'form-select'}),
            'lot': forms.Select(attrs={'class': 'form-select'}),
            'quantite_retournee': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'motif': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'remis_en_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
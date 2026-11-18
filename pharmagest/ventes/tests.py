from django.test import TestCase, Client
from django.urls import reverse
from utilisateurs.models import Utilisateur
from catalogue.models import Categorie, Medicament
from achats_stock.models import LotStock
from ventes.models import Vente

class VentesTests(TestCase):
    def setUp(self):
        # Création d'un utilisateur (caissier)
        self.user = Utilisateur.objects.create_user(
            username='caissier_test', password='password123', role='CAISSIER'
        )
        # Création d'un produit et de son lot
        self.categorie = Categorie.objects.create(nom="Test Cat")
        self.medicament = Medicament.objects.create(
            nom_commercial="Medicament Test", categorie=self.categorie,
            prix_achat=100, prix_vente=200
        )
        self.lot = LotStock.objects.create(
            medicament=self.medicament, numero_lot="LOT-01",
            date_peremption="2030-01-01", quantite_actuelle=10
        )
        self.client = Client()
        self.client.login(username='caissier_test', password='password123')

    # TEST 1 : Accès refusé sans permission
    def test_acces_refuse_catalogue(self):
        response = self.client.get(reverse('catalogue:medicament_list'))
        # Le caissier ne peut pas accéder au catalogue (redirigé vers login)
        self.assertEqual(response.status_code, 302)

    # TEST 2 : Vente réussie
    def test_vente_reussie(self):
        response = self.client.post(reverse('ventes:vente_add'), {
            'lot': self.lot.id,
            'quantite': 2,
            'mode_paiement': 'ESPECES'
        })
        self.assertEqual(response.status_code, 302) # Redirection après succès
        self.lot.refresh_from_db()
        self.assertEqual(self.lot.quantite_actuelle, 8) # 10 - 2

    # TEST 3 : Vente refusée si stock insuffisant
    def test_vente_stock_insuffisant(self):
        response = self.client.post(reverse('ventes:vente_add'), {
            'lot': self.lot.id,
            'quantite': 20, # Plus que les 10 disponibles
            'mode_paiement': 'ESPECES'
        })
        self.lot.refresh_from_db()
        self.assertEqual(self.lot.quantite_actuelle, 10) # Le stock n'a pas bougé

    # TEST 4 : Connexion requise
    def test_acces_sans_connexion(self):
        self.client.logout()
        response = self.client.get(reverse('ventes:vente_list'))
        self.assertEqual(response.status_code, 302) # Redirige vers login

    # TEST 5 : Création d'un médicament (Admin)
    def test_creation_medicament(self):
        self.user.role = 'PHARMACIEN'
        self.user.save()
        self.client.logout()
        self.client.login(username='caissier_test', password='password123')
        
        response = self.client.post(reverse('catalogue:medicament_add'), {
            'nom_commercial': 'Nouveau Med',
            'categorie': self.categorie.id,
            'forme': 'COMPRIME',
            'prix_achat': 500,
            'prix_vente': 1000,
            'seuil_alerte': 5,
            'statut': 'ACTIF'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Medicament.objects.count(), 2)
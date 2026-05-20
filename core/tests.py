from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import Vehicule, Trajet, PreferenceTrajet, Reservation, StatutTrajet, StatutReservation, StatutCompte
import datetime

User = get_user_model()

class CovoiturageTestCase(TestCase):
    def setUp(self):
        # Create users
        self.driver = User.objects.create_user(
            username='driver1',
            email='driver@test.com',
            password='testpassword',
            first_name='Moez',
            last_name='Driver',
            telephone='12345678',
            numeroPermis='12345'
        )
        
        self.passenger = User.objects.create_user(
            username='passenger1',
            email='passenger@test.com',
            password='testpassword',
            first_name='Amira',
            last_name='Passager',
            telephone='87654321'
        )

        # Create vehicle
        self.vehicle = Vehicule.objects.create(
            marque='Kia',
            modele='Rio',
            couleur='Blanche',
            immatriculation='188 TUN 9999',
            typeVehicule='Citadine',
            nombrePlaces=4,
            owner=self.driver
        )

        # Create preferences
        self.prefs = PreferenceTrajet.objects.create(
            nonFumeur=True,
            femmesUniquement=False
        )

        # Create ride
        self.ride = Trajet.objects.create(
            villeDepart='Tunis',
            villeArrivee='Sousse',
            dateTrajet=timezone.now().date() + datetime.timedelta(days=1),
            heureDepart=datetime.time(10, 0),
            prixParPlace=15.00,
            placesDisponibles=4,
            driver=self.driver,
            vehicle=self.vehicle,
            preferences=self.prefs
        )

    def test_places_restantes_calculation(self):
        # Initially, 4 seats should be available
        self.assertEqual(self.ride.calculerPlacesRestantes(), 4)

        # Create booking, initially EN_ATTENTE (pending) - should NOT decrease places
        booking = Reservation.objects.create(
            nombrePlacesReservees=2,
            statut=StatutReservation.EN_ATTENTE,
            passenger=self.passenger,
            ride=self.ride
        )
        self.assertEqual(self.ride.calculerPlacesRestantes(), 4)

        # Confirm booking - SHOULD decrease places
        booking.statut = StatutReservation.CONFIRMEE
        booking.save()
        self.assertEqual(self.ride.calculerPlacesRestantes(), 2)

    def test_user_ratings_calculation(self):
        # Create booking
        booking = Reservation.objects.create(
            nombrePlacesReservees=1,
            statut=StatutReservation.CONFIRMEE,
            passenger=self.passenger,
            ride=self.ride,
            note=5,
            commentaire="Excellent trajet !",
            dateAvis=timezone.now()
        )
        
        # Driver should have average rating of 5.0 and 1 review
        self.assertEqual(self.driver.noteMoyenne, 5.0)
        self.assertEqual(self.driver.nombreAvis, 1)

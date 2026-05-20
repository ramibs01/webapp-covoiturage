from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import User, Vehicule, Trajet, PreferenceTrajet, Reservation, Message, StatutTrajet, StatutReservation, StatutCompte
from django.utils import timezone
import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = "Populate the database with sample Tunisian covoiturage data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # 1. Clear existing data
        Reservation.objects.all().delete()
        Message.objects.all().delete()
        Trajet.objects.all().delete()
        Vehicule.objects.all().delete()
        User.objects.all().delete()

        # 2. Create Superuser (Admin)
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@covoiturage.tn',
            password='adminpassword',
            first_name='Rami',
            last_name='Ben Slima',
            telephone='98765432',
            adresse='Tunis, Tunisie'
        )
        self.stdout.write("Created Admin: admin / adminpassword")

        # 3. Create Drivers
        driver1 = User.objects.create_user(
            username='yessin',
            email='yessin@covoiturage.tn',
            password='password123',
            first_name='Yessin',
            last_name='Bahri',
            telephone='99123456',
            adresse='Sousse, Tunisie',
            numeroPermis='26/112233',
            statut=StatutCompte.ACTIF
        )
        
        driver2 = User.objects.create_user(
            username='aziz',
            email='aziz@covoiturage.tn',
            password='password123',
            first_name='Aziz',
            last_name='Zouari',
            telephone='98223344',
            adresse='Sfax, Tunisie',
            numeroPermis='25/445566',
            statut=StatutCompte.ACTIF
        )

        # 4. Create Passengers
        passenger1 = User.objects.create_user(
            username='ahmad',
            email='ahmad@covoiturage.tn',
            password='password123',
            first_name='Ahmad',
            last_name='Borcheni',
            telephone='97334455',
            adresse='Tunis, Tunisie',
            statut=StatutCompte.ACTIF
        )

        passenger2 = User.objects.create_user(
            username='youssef',
            email='youssef@covoiturage.tn',
            password='password123',
            first_name='Youssef',
            last_name='Chaari',
            telephone='95445566',
            adresse='Nabeul, Tunisie',
            statut=StatutCompte.ACTIF
        )

        self.stdout.write("Created demo users: yessin (driver), aziz (driver), ahmad (passenger), youssef (passenger) - password: password123")

        # 5. Create Vehicles
        v1 = Vehicule.objects.create(
            marque='Peugeot',
            modele='208',
            couleur='Noir',
            immatriculation='180 TUN 1234',
            typeVehicule='Citadine',
            nombrePlaces=4,
            owner=driver1
        )

        v2 = Vehicule.objects.create(
            marque='Volkswagen',
            modele='Golf 7',
            couleur='Gris',
            immatriculation='210 TUN 5678',
            typeVehicule='Compacte',
            nombrePlaces=4,
            owner=driver2
        )
        self.stdout.write("Created vehicles for drivers.")

        # 6. Create Rides
        today = datetime.date.today()
        
        # Ride 1: Tunis -> Sousse (Open)
        pref1 = PreferenceTrajet.objects.create(
            femmesUniquement=False,
            nonFumeur=True,
            accepteAnimaux=False,
            accepteBagagesVolumineux=True,
            musiqueAutorisee=True,
            pauseCafe=False
        )
        ride1 = Trajet.objects.create(
            villeDepart='Tunis',
            villeArrivee='Sousse',
            dateTrajet=today + datetime.timedelta(days=1),
            heureDepart=datetime.time(8, 30),
            prixParPlace=Decimal('12.00'),
            placesDisponibles=4,
            description="Départ de Bab Alioua, coffre spacieux pour bagages.",
            statut=StatutTrajet.OUVERT,
            driver=driver1,
            vehicle=v1,
            preferences=pref1
        )

        # Ride 2: Tunis -> Sfax (Open)
        pref2 = PreferenceTrajet.objects.create(
            femmesUniquement=False,
            nonFumeur=True,
            accepteAnimaux=True,
            accepteBagagesVolumineux=True,
            musiqueAutorisee=True,
            pauseCafe=True
        )
        ride2 = Trajet.objects.create(
            villeDepart='Tunis',
            villeArrivee='Sfax',
            dateTrajet=today + datetime.timedelta(days=2),
            heureDepart=datetime.time(14, 0),
            prixParPlace=Decimal('22.00'),
            placesDisponibles=4,
            description="Arrêt à la station d'autoroute de Sousse pour pause café.",
            statut=StatutTrajet.OUVERT,
            driver=driver2,
            vehicle=v2,
            preferences=pref2
        )

        # Ride 3: Sfax -> Tunis (Complet / Completed with reviews)
        pref3 = PreferenceTrajet.objects.create(
            femmesUniquement=True,
            nonFumeur=True,
            accepteAnimaux=False,
            accepteBagagesVolumineux=False,
            musiqueAutorisee=False,
            pauseCafe=False
        )
        ride3 = Trajet.objects.create(
            villeDepart='Sfax',
            villeArrivee='Tunis',
            dateTrajet=today - datetime.timedelta(days=3),
            heureDepart=datetime.time(7, 0),
            prixParPlace=Decimal('20.00'),
            placesDisponibles=4,
            description="Trajet 100% femmes uniquement pour des raisons de confort personnel.",
            statut=StatutTrajet.COMPLET,
            driver=driver2,
            vehicle=v2,
            preferences=pref3
        )

        self.stdout.write("Created rides.")

        # 7. Create Reservations (Bookings)
        # Reservation on Ride 1 (Pending)
        res1 = Reservation.objects.create(
            nombrePlacesReservees=2,
            statut=StatutReservation.EN_ATTENTE,
            passenger=passenger1,
            ride=ride1
        )

        # Reservation on Ride 2 (Confirmed)
        res2 = Reservation.objects.create(
            nombrePlacesReservees=1,
            statut=StatutReservation.CONFIRMEE,
            passenger=passenger2,
            ride=ride2
        )

        # Reservation on Ride 3 (Confirmed, completed, reviewed)
        res3 = Reservation.objects.create(
            nombrePlacesReservees=2,
            statut=StatutReservation.CONFIRMEE,
            passenger=passenger1,
            ride=ride3,
            note=5,
            commentaire="Chauffeur très ponctuelle et voiture très propre. Je recommande !",
            dateAvis=timezone.now() - datetime.timedelta(days=2)
        )
        self.stdout.write("Created reservations and reviews.")

        # 8. Create Messages
        Message.objects.create(
            contenu="Bonjour, le départ de Tunis se fait d'où exactement ?",
            expediteur=passenger1,
            destinataire=driver1,
            dateEnvoi=timezone.now() - datetime.timedelta(hours=5)
        )
        Message.objects.create(
            contenu="Bonjour, rendez-vous devant la station Bab Alioua à 8h20.",
            expediteur=driver1,
            destinataire=passenger1,
            dateEnvoi=timezone.now() - datetime.timedelta(hours=4)
        )
        self.stdout.write("Created message conversation.")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

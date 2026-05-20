from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal

# Statut Enums matching the class diagram
class StatutCompte(models.TextChoices):
    ACTIF = 'ACTIF', 'Actif'
    DESACTIVE = 'DESACTIVE', 'Désactivé'
    SUSPENDU = 'SUSPENDU', 'Suspendu'

class StatutTrajet(models.TextChoices):
    OUVERT = 'OUVERT', 'Ouvert'
    COMPLET = 'COMPLET', 'Complet'
    ANNULE = 'ANNULE', 'Annulé'
    TERMINE = 'TERMINE', 'Terminé'

class StatutReservation(models.TextChoices):
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    CONFIRMEE = 'CONFIRMEE', 'Confirmée'
    REFUSEE = 'REFUSEE', 'Refusée'
    ANNULEE = 'ANNULEE', 'Annulée'

class User(AbstractUser):
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    adresse = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse")
    photoProfil = models.ImageField(upload_to='profiles/', blank=True, null=True, default='profiles/default.png', verbose_name="Photo de profil")
    statut = models.CharField(max_length=20, choices=StatutCompte.choices, default=StatutCompte.ACTIF, verbose_name="Statut du compte")
    
    # Fields specific to Conducteur (subclass logic merged in standard Django style)
    numeroPermis = models.CharField(max_length=50, blank=True, null=True, verbose_name="Numéro de permis")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    @property
    def noteMoyenne(self):
        # We average the notes left on confirmed reservations for rides driven by this user
        reservations_with_reviews = Reservation.objects.filter(
            ride__driver=self,
            statut=StatutReservation.CONFIRMEE,
            note__isnull=False
        )
        if not reservations_with_reviews.exists():
            return 0.0
        total = sum(res.note for res in reservations_with_reviews)
        return round(total / reservations_with_reviews.count(), 1)

    @property
    def nombreAvis(self):
        return Reservation.objects.filter(
            ride__driver=self,
            statut=StatutReservation.CONFIRMEE,
            note__isnull=False
        ).count()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Vehicule(models.Model):
    marque = models.CharField(max_length=50, verbose_name="Marque")
    modele = models.CharField(max_length=50, verbose_name="Modèle")
    couleur = models.CharField(max_length=30, verbose_name="Couleur")
    immatriculation = models.CharField(max_length=50, verbose_name="Immatriculation")
    typeVehicule = models.CharField(max_length=50, verbose_name="Type de Véhicule")
    nombrePlaces = models.IntegerField(verbose_name="Nombre de places")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles', verbose_name="Propriétaire")

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.immatriculation})"


class PreferenceTrajet(models.Model):
    femmesUniquement = models.BooleanField(default=False, verbose_name="Femmes uniquement")
    nonFumeur = models.BooleanField(default=False, verbose_name="Non-fumeur")
    accepteAnimaux = models.BooleanField(default=False, verbose_name="Accepte les animaux")
    accepteBagagesVolumineux = models.BooleanField(default=False, verbose_name="Accepte les bagages volumineux")
    musiqueAutorisee = models.BooleanField(default=False, verbose_name="Musique autorisée")
    pauseCafe = models.BooleanField(default=False, verbose_name="Pause café")

    def __str__(self):
        prefs = []
        if self.femmesUniquement: prefs.append("Femmes uniquement")
        if self.nonFumeur: prefs.append("Non-fumeur")
        if self.accepteAnimaux: prefs.append("Animaux acceptés")
        if self.accepteBagagesVolumineux: prefs.append("Grands bagages")
        if self.musiqueAutorisee: prefs.append("Musique")
        if self.pauseCafe: prefs.append("Pause café")
        return ", ".join(prefs) if prefs else "Aucune préférence particulière"


class Trajet(models.Model):
    villeDepart = models.CharField(max_length=100, verbose_name="Ville de départ")
    villeArrivee = models.CharField(max_length=100, verbose_name="Ville d'arrivée")
    dateTrajet = models.DateField(verbose_name="Date du trajet")
    heureDepart = models.TimeField(verbose_name="Heure de départ")
    prixParPlace = models.DecimalField(max_length=10, max_digits=10, decimal_places=2, verbose_name="Prix par place (TND)")
    placesDisponibles = models.IntegerField(verbose_name="Places initiales disponibles")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    statut = models.CharField(max_length=20, choices=StatutTrajet.choices, default=StatutTrajet.OUVERT, verbose_name="Statut")
    
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_driven', verbose_name="Conducteur")
    vehicle = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True, related_name='rides', verbose_name="Véhicule")
    preferences = models.OneToOneField(PreferenceTrajet, on_delete=models.CASCADE, related_name='ride', verbose_name="Préférences")

    class Meta:
        verbose_name = "Trajet"
        verbose_name_plural = "Trajets"

    def calculerPlacesRestantes(self):
        confirmed_seats = self.reservations.filter(statut=StatutReservation.CONFIRMEE).aggregate(
            total=models.Sum('nombrePlacesReservees')
        )['total'] or 0
        return max(0, self.placesDisponibles - confirmed_seats)

    def is_complet(self):
        return self.calculerPlacesRestantes() == 0

    def update_status(self):
        if self.statut == StatutTrajet.OUVERT and self.is_complet():
            self.statut = StatutTrajet.COMPLET
            self.save()
        elif self.statut == StatutTrajet.COMPLET and not self.is_complet():
            self.statut = StatutTrajet.OUVERT
            self.save()

    def __str__(self):
        return f"{self.villeDepart} -> {self.villeArrivee} le {self.dateTrajet} à {self.heureDepart}"


class Reservation(models.Model):
    dateReservation = models.DateTimeField(auto_now_add=True, verbose_name="Date de réservation")
    nombrePlacesReservees = models.IntegerField(verbose_name="Places réservées")
    prixTotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix total (TND)")
    statut = models.CharField(max_length=20, choices=StatutReservation.choices, default=StatutReservation.EN_ATTENTE, verbose_name="Statut")
    
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', verbose_name="Passager")
    ride = models.ForeignKey(Trajet, on_delete=models.CASCADE, related_name='reservations', verbose_name="Trajet")
    
    # Review details (rating & review directly inside Reservation model as per class diagram)
    note = models.IntegerField(blank=True, null=True, choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Note (1-5)")
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire / Avis")
    dateAvis = models.DateTimeField(blank=True, null=True, verbose_name="Date de l'avis")

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def save(self, *args, **kwargs):
        if not self.prixTotal and self.ride:
            self.prixTotal = Decimal(str(self.nombrePlacesReservees)) * Decimal(str(self.ride.prixParPlace))
        super().save(*args, **kwargs)
        # Update ride completion status if appropriate
        if self.ride:
            self.ride.update_status()

    def __str__(self):
        return f"Réservation #{self.id} - {self.passenger.first_name} pour {self.ride}"


class Message(models.Model):
    contenu = models.TextField(verbose_name="Contenu")
    dateEnvoi = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Expéditeur")
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name="Destinataire")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['dateEnvoi']

    def __str__(self):
        return f"De {self.expediteur.username} à {self.destinataire.username} le {self.dateEnvoi}"


# Statistiques Helper Class to match class diagram
class Statistiques:
    @staticmethod
    def get_stats():
        return {
            'nombreUtilisateurs': User.objects.count(),
            'nombreTrajets': Trajet.objects.count(),
            'nombreReservations': Reservation.objects.count(),
            'nombreCommentaires': Reservation.objects.filter(note__isnull=False).count(),
        }

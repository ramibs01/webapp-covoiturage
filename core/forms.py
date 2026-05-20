from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Vehicule, Trajet, PreferenceTrajet, Reservation, Message

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Adresse Email")
    telephone = forms.CharField(max_length=20, required=True, label="Téléphone")
    adresse = forms.CharField(max_length=255, required=False, label="Adresse")
    photoProfil = forms.ImageField(required=False, label="Photo de profil")
    numeroPermis = forms.CharField(max_length=50, required=False, label="Numéro de permis (requis pour être conducteur)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'telephone', 'adresse', 'photoProfil', 'numeroPermis')


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telephone', 'adresse', 'photoProfil', 'numeroPermis']


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['marque', 'modele', 'couleur', 'immatriculation', 'typeVehicule', 'nombrePlaces']


class TrajetForm(forms.ModelForm):
    class Meta:
        model = Trajet
        fields = ['villeDepart', 'villeArrivee', 'dateTrajet', 'heureDepart', 'prixParPlace', 'placesDisponibles', 'description', 'vehicle']
        widgets = {
            'dateTrajet': forms.DateInput(attrs={'type': 'date'}),
            'heureDepart': forms.TimeInput(attrs={'type': 'time'}),
        }


class PreferenceTrajetForm(forms.ModelForm):
    class Meta:
        model = PreferenceTrajet
        fields = ['femmesUniquement', 'nonFumeur', 'accepteAnimaux', 'accepteBagagesVolumineux', 'musiqueAutorisee', 'pauseCafe']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['nombrePlacesReservees']
        widgets = {
            'nombrePlacesReservees': forms.NumberInput(attrs={'min': 1, 'class': 'w-full px-3 py-2 border rounded-md'})
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'commentaire': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border rounded-md', 'placeholder': 'Votre avis...'}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Écrivez un message...', 'class': 'w-full p-2 border rounded-md'}),
        }

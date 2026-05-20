from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
from .models import User, Vehicule, Trajet, PreferenceTrajet, Reservation, Message, Statistiques, StatutTrajet, StatutReservation, StatutCompte
from .forms import CustomUserCreationForm, ProfileUpdateForm, VehiculeForm, TrajetForm, PreferenceTrajetForm, BookingForm, ReviewForm, MessageForm

def home(request):
    recent_rides = Trajet.objects.filter(
        statut=StatutTrajet.OUVERT,
        dateTrajet__gte=timezone.now().date()
    ).order_by('dateTrajet', 'heureDepart')[:6]
    
    stats = Statistiques.get_stats()
    
    return render(request, 'core/home.html', {
        'recent_rides': recent_rides,
        'stats': stats
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue sur Covoiturage Tunisie.")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/auth.html', {'form': form, 'action': 'register'})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.statut == StatutCompte.DESACTIVE or user.statut == StatutCompte.SUSPENDU:
                messages.error(request, "Votre compte a été désactivé ou suspendu.")
                return redirect('login')
            login(request, user)
            messages.success(request, f"Ravi de vous revoir, {user.first_name} !")
            return redirect('home')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'core/auth.html', {'action': 'login'})


def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')


def search_results(request):
    departure = request.GET.get('departure', '').strip()
    destination = request.GET.get('destination', '').strip()
    date_str = request.GET.get('date', '').strip()

    rides = Trajet.objects.filter(statut=StatutTrajet.OUVERT, dateTrajet__gte=timezone.now().date())

    if departure:
        rides = rides.filter(villeDepart__icontains=departure)
    if destination:
        rides = rides.filter(villeArrivee__icontains=destination)
    if date_str:
        rides = rides.filter(dateTrajet=date_str)

    # Advanced Filters
    max_price = request.GET.get('max_price')
    non_fumeur = request.GET.get('non_fumeur')
    femmes_uniquement = request.GET.get('femmes_uniquement')
    accepte_animaux = request.GET.get('accepte_animaux')
    bagages = request.GET.get('bagages')

    if max_price:
        try:
            rides = rides.filter(prixParPlace__lte=Decimal(max_price))
        except:
            pass

    if non_fumeur:
        rides = rides.filter(preferences__nonFumeur=True)
    if femmes_uniquement:
        rides = rides.filter(preferences__femmesUniquement=True)
    if accepte_animaux:
        rides = rides.filter(preferences__accepteAnimaux=True)
    if bagages:
        rides = rides.filter(preferences__accepteBagagesVolumineux=True)

    # Calculate remaining seats dynamically for UI
    for ride in rides:
        ride.places_restantes = ride.calculerPlacesRestantes()

    return render(request, 'core/search_results.html', {
        'rides': rides,
        'departure': departure,
        'destination': destination,
        'date': date_str,
        'max_price': max_price,
        'non_fumeur': non_fumeur,
        'femmes_uniquement': femmes_uniquement,
        'accepte_animaux': accepte_animaux,
        'bagages': bagages,
    })


def ride_detail(request, pk):
    ride = get_object_or_404(Trajet, pk=pk)
    driver = ride.driver
    places_restantes = ride.calculerPlacesRestantes()
    
    # Reviews
    reviews = Reservation.objects.filter(
        ride__driver=driver,
        statut=StatutReservation.CONFIRMEE,
        note__isnull=False
    ).order_by('-dateAvis')

    # Booking Form
    booking_form = BookingForm()
    
    # Message Form
    message_form = MessageForm()

    return render(request, 'core/ride_detail.html', {
        'ride': ride,
        'places_restantes': places_restantes,
        'reviews': reviews,
        'booking_form': booking_form,
        'message_form': message_form,
    })


@login_required
def publish_ride(request):
    if not request.user.numeroPermis:
        messages.warning(request, "Veuillez d'abord configurer votre numéro de permis dans votre profil pour publier un trajet.")
        return redirect('profile')

    # Check if user has registered vehicles
    vehicles = request.user.vehicles.all()
    if not vehicles.exists():
        messages.warning(request, "Veuillez d'abord ajouter un véhicule dans votre profil avant de publier un trajet.")
        return redirect('profile')

    if request.method == 'POST':
        trajet_form = TrajetForm(request.POST)
        pref_form = PreferenceTrajetForm(request.POST)
        if trajet_form.is_valid() and pref_form.is_valid():
            preferences = pref_form.save()
            trajet = trajet_form.save(commit=False)
            trajet.driver = request.user
            trajet.preferences = preferences
            trajet.save()
            messages.success(request, "Votre trajet a été publié avec succès !")
            return redirect('dashboard')
    else:
        trajet_form = TrajetForm()
        # Prefill vehicles for the logged in user
        trajet_form.fields['vehicle'].queryset = vehicles
        pref_form = PreferenceTrajetForm()

    return render(request, 'core/publish_ride.html', {
        'trajet_form': trajet_form,
        'pref_form': pref_form,
    })


@login_required
def edit_ride(request, pk):
    ride = get_object_or_404(Trajet, pk=pk, driver=request.user)
    if request.method == 'POST':
        trajet_form = TrajetForm(request.POST, instance=ride)
        pref_form = PreferenceTrajetForm(request.POST, instance=ride.preferences)
        if trajet_form.is_valid() and pref_form.is_valid():
            pref_form.save()
            trajet_form.save()
            messages.success(request, "Trajet modifié avec succès.")
            return redirect('dashboard')
    else:
        trajet_form = TrajetForm(instance=ride)
        trajet_form.fields['vehicle'].queryset = request.user.vehicles.all()
        pref_form = PreferenceTrajetForm(instance=ride.preferences)
    return render(request, 'core/publish_ride.html', {
        'trajet_form': trajet_form,
        'pref_form': pref_form,
        'editing': True,
    })


@login_required
def cancel_ride(request, pk):
    ride = get_object_or_404(Trajet, pk=pk, driver=request.user)
    ride.statut = StatutTrajet.ANNULE
    ride.save()
    
    # Cancel all reservations for this ride
    ride.reservations.filter(
        statut__in=[StatutReservation.EN_ATTENTE, StatutReservation.CONFIRMEE]
    ).update(statut=StatutReservation.ANNULEE)
    
    messages.success(request, "Trajet annulé avec succès.")
    return redirect('dashboard')


@login_required
def request_booking(request, pk):
    ride = get_object_or_404(Trajet, pk=pk)
    if ride.driver == request.user:
        messages.error(request, "Vous ne pouvez pas réserver votre propre trajet.")
        return redirect('ride_detail', pk=pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seats_requested = form.cleaned_data['nombrePlacesReservees']
            places_restantes = ride.calculerPlacesRestantes()

            if seats_requested > places_restantes:
                messages.error(request, f"Désolé, il ne reste que {places_restantes} places disponibles.")
                return redirect('ride_detail', pk=pk)

            booking = form.save(commit=False)
            booking.passenger = request.user
            booking.ride = ride
            booking.statut = StatutReservation.EN_ATTENTE
            booking.save()
            
            messages.success(request, "Votre demande de réservation a été envoyée au conducteur !")
            return redirect('dashboard')
    return redirect('ride_detail', pk=pk)


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Reservation, pk=pk, passenger=request.user)
    booking.statut = StatutReservation.ANNULEE
    booking.save()
    # Update ride status in case it becomes open again
    booking.ride.update_status()
    messages.success(request, "Réservation annulée.")
    return redirect('dashboard')


@login_required
def approve_booking(request, pk):
    booking = get_object_or_404(Reservation, pk=pk, ride__driver=request.user)
    places_restantes = booking.ride.calculerPlacesRestantes()

    if booking.nombrePlacesReservees > places_restantes:
        messages.error(request, "Impossible de confirmer la réservation. Plus assez de places disponibles.")
        booking.statut = StatutReservation.REFUSEE
        booking.save()
        return redirect('dashboard')

    booking.statut = StatutReservation.CONFIRMEE
    booking.save()
    messages.success(request, "Réservation acceptée.")
    return redirect('dashboard')


@login_required
def reject_booking(request, pk):
    booking = get_object_or_404(Reservation, pk=pk, ride__driver=request.user)
    booking.statut = StatutReservation.REFUSEE
    booking.save()
    messages.success(request, "Réservation refusée.")
    return redirect('dashboard')


@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'profile_submit' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profil mis à jour.")
                return redirect('profile')
        elif 'vehicle_submit' in request.POST:
            vehicle_form = VehiculeForm(request.POST)
            if vehicle_form.is_valid():
                vehicle = vehicle_form.save(commit=False)
                vehicle.owner = request.user
                vehicle.save()
                messages.success(request, "Véhicule ajouté avec succès.")
                return redirect('profile')
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        vehicle_form = VehiculeForm()
        
    vehicles = request.user.vehicles.all()
    return render(request, 'core/profile.html', {
        'profile_form': profile_form,
        'vehicle_form': vehicle_form,
        'vehicles': vehicles,
    })


@login_required
def dashboard(request):
    # Driver data
    published_rides = Trajet.objects.filter(driver=request.user).order_by('-dateTrajet', '-heureDepart')
    pending_approvals = Reservation.objects.filter(
        ride__driver=request.user,
        statut=StatutReservation.EN_ATTENTE
    ).order_by('-dateReservation')
    
    # Passenger data
    my_bookings = Reservation.objects.filter(passenger=request.user).order_by('-dateReservation')
    
    return render(request, 'core/dashboard.html', {
        'published_rides': published_rides,
        'pending_approvals': pending_approvals,
        'my_bookings': my_bookings,
        'StatutReservation': StatutReservation,
        'StatutTrajet': StatutTrajet,
    })


@login_required
def leave_review(request, pk):
    booking = get_object_or_404(Reservation, pk=pk, passenger=request.user)
    if booking.statut != StatutReservation.CONFIRMEE:
        messages.error(request, "Vous ne pouvez laisser un avis que pour les réservations confirmées.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=booking)
        if form.is_valid():
            review = form.save(commit=False)
            review.dateAvis = timezone.now()
            review.save()
            messages.success(request, "Votre avis a été enregistré !")
            return redirect('dashboard')
    else:
        form = ReviewForm(instance=booking)
        
    return render(request, 'core/leave_review.html', {
        'form': form,
        'booking': booking,
    })


@login_required
def send_message_view(request, recipient_id):
    recipient = get_object_or_404(User, pk=recipient_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.expediteur = request.user
            message.destinataire = recipient
            message.save()
            messages.success(request, "Message envoyé !")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def inbox_view(request):
    # Get all users the user has conversed with
    sent_to = Message.objects.filter(expediteur=request.user).values_list('destinataire', flat=True)
    received_from = Message.objects.filter(destinataire=request.user).values_list('expediteur', flat=True)
    contact_ids = set(list(sent_to) + list(received_from))
    
    contacts = User.objects.filter(id__in=contact_ids).exclude(id=request.user.id)
    
    # Active conversation
    active_contact_id = request.GET.get('contact')
    active_contact = None
    messages_list = []
    
    if active_contact_id:
        active_contact = get_object_or_404(User, id=active_contact_id)
        messages_list = Message.objects.filter(
            (Q(expediteur=request.user) & Q(destinataire=active_contact)) |
            (Q(expediteur=active_contact) & Q(destinataire=request.user))
        ).order_by('dateEnvoi')
        
    form = MessageForm()
    
    return render(request, 'core/inbox.html', {
        'contacts': contacts,
        'active_contact': active_contact,
        'messages_list': messages_list,
        'form': form,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('home')
        
    stats = Statistiques.get_stats()
    users = User.objects.all().order_by('-date_joined')
    rides = Trajet.objects.all().order_by('-dateTrajet')
    
    return render(request, 'core/admin_dashboard.html', {
        'stats': stats,
        'users': users,
        'rides': rides,
        'StatutCompte': StatutCompte,
    })


@login_required
def admin_toggle_user(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Accès refusé.")
        return redirect('home')
        
    user = get_object_or_404(User, pk=pk)
    if user.statut == StatutCompte.ACTIF:
        user.statut = StatutCompte.DESACTIVE
    else:
        user.statut = StatutCompte.ACTIF
    user.save()
    messages.success(request, f"Statut de l'utilisateur {user.username} mis à jour.")
    return redirect('admin_dashboard')

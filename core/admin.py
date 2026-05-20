from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Vehicule, Trajet, PreferenceTrajet, Reservation, Message

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('telephone', 'adresse', 'photoProfil', 'statut', 'numeroPermis')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('first_name', 'last_name', 'email', 'telephone', 'adresse', 'photoProfil', 'statut', 'numeroPermis')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'telephone', 'statut', 'is_staff']
    list_filter = ['statut', 'is_staff', 'is_superuser']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Vehicule)
admin.site.register(Trajet)
admin.site.register(PreferenceTrajet)
admin.site.register(Reservation)
admin.site.register(Message)

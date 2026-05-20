from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_results, name='search'),
    path('ride/<int:pk>/', views.ride_detail, name='ride_detail'),
    path('ride/publish/', views.publish_ride, name='publish_ride'),
    path('ride/<int:pk>/edit/', views.edit_ride, name='edit_ride'),
    path('ride/<int:pk>/cancel/', views.cancel_ride, name='cancel_ride'),
    path('ride/<int:pk>/book/', views.request_booking, name='request_booking'),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:pk>/approve/', views.approve_booking, name='approve_booking'),
    path('booking/<int:pk>/reject/', views.reject_booking, name='reject_booking'),
    path('booking/<int:pk>/review/', views.leave_review, name='leave_review'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('message/send/<int:recipient_id>/', views.send_message_view, name='send_message'),
    path('inbox/', views.inbox_view, name='inbox'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/toggle-user/<int:pk>/', views.admin_toggle_user, name='admin_toggle_user'),
]

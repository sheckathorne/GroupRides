from django.urls import path
from django.contrib.auth import views as auth_views
from users import views as user_views
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path('clubs/<int:club_id>/', views.club_home, name="club_home"),
    path('<int:event_occurence_id>/ride_registration/delete/', views.delete_ride_reigstration, name="delete_registration"),
    path('<int:event_occurence_id>/ride_registration/create/', views.create_ride_registration, name="create_registration"),
    path('<int:event_occurence_member_id>/ride/attendees', views.ride_attendees, name="ride_attendees")
]

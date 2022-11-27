from django.urls import path
from . import views
from .views import EventComments
from .decorators import user_is_ride_member

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("my_rides/", views.my_rides, name="my_rides"),
    path("available_rides/", views.available_rides_clubs, name="available_rides_clubs"),
    path("<int:club_id>/available_rides/club/<slug:slug>/", views.available_rides, name="available_rides"),
    path(
        "<int:club_id>/available_rides/club/<slug:slug>/<str:group_classification>/",
        views.available_rides,
        name="available_rides_group"),
    path('clubs/<int:club_id>/', views.club_home, name="club_home"),
    path(
        '<int:event_occurence_id>/ride_registration/delete/',
        views.delete_ride_reigstration,
        name="delete_registration"),
    path(
        '<int:event_occurence_id>/ride_registration/create/',
        views.create_ride_registration,
        name="create_registration"),
    path('<int:event_occurence_member_id>/ride/attendees', views.ride_attendees, name="ride_attendees"),
    path('<int:event_occurence_id>/ride/comments', user_is_ride_member(EventComments.as_view()), name="ride_comments"),
    path(
        '<int:event_occurence_id>/ride/comments/click',
        views.event_occurence_comments_click,
        name="ride_comments_click")
]

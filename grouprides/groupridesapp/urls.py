from django.urls import path, include
from . import views
from .views import EventComments, CreateClub, CreateEvent, CreateRoute
from .decorators import user_is_ride_member

urlpatterns = [
    path("", views.homepage, name="homepage"),

    # Rides
    path("my_rides/", views.my_rides, name="my_rides"),
    path("available_rides/", views.available_rides, name="available_rides"),
    path('<int:event_occurence_id>/ride_registration/', include([
        path('delete/', views.delete_ride_registration, name="delete_registration"),
        path('create/', views.create_ride_registration, name="create_registration"),
    ])),

    # Ride Comments
    path('<int:event_occurence_id>/ride/comments/', include([
        path('', user_is_ride_member(EventComments.as_view()), name="ride_comments"),
        path('click/', views.event_occurence_comments_click, name="ride_comments_click")
    ])),

    path('<int:event_occurence_member_id>/ride/attendees/', views.ride_attendees, name="ride_attendees"),

    path('create_club/', CreateClub.as_view(), name="create_club"),
    path('create_event/', CreateEvent.as_view(), name="create_event"),
    path('create_route/', CreateRoute.as_view(), name="create_route")
]

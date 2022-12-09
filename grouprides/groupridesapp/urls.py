from django.urls import path, include
from . import views
from .views import EventComments, CreateClub, CreateEvent, CreateRoute
from .decorators import user_is_ride_member

urlpatterns = [
    path("", views.homepage, name="homepage"),

    # Rides
    path("rides/", include([
        path("", views.available_rides, name="available_rides"),
        path("registered/", views.my_rides, name="my_rides"),

        # Ride Registration
        path("registration/<int:event_occurence_id>/", include([
            path("delete/", views.delete_ride_registration, name="delete_registration"),
            path("create/", views.create_ride_registration, name="create_registration"),
        ])),

        # Event Create
        path("create/", CreateEvent.as_view(), name="create_event"),

        # Ride Comments
        path("<int:event_occurence_id>/comments/", include([
            path("", user_is_ride_member(EventComments.as_view()), name="ride_comments"),
            path("click/", views.event_occurence_comments_click, name="ride_comments_click")
        ])),

        path("<int:event_occurence_member_id>/attendees/",views.ride_attendees, name="ride_attendees"),
    ])),

    # Clubs
    path("clubs/", include([
        path("joined/", views.my_clubs, name="my_clubs"),
        path("create/", CreateClub.as_view(), name="create_club"),
        path("members/", include([
            path("<str:_slug>-<int:club_id>/management/", views.club_member_management, name="club_member_management")
        ]))
    ])),

    # Routes
    path("create_route/", CreateRoute.as_view(), name="create_route")
]

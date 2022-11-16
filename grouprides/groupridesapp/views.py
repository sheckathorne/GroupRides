import datetime

from django.shortcuts import render
from .models import Club, Event, EventOccurence, EventOccurenceMember


def homepage(request):
    next_week = datetime.date.today() + datetime.timedelta(days=21)
    my_upcoming_rides = EventOccurenceMember.objects.filter(
        user=request.user,
        event_occurence__ride_date__lte=next_week
    )

    my_clubs = Club.objects.filter(
        clubmembership__user=request.user
    )

    return render(request=request,
                  template_name="groupridesapp/home.html",
                  context={
                    "my_clubs": my_clubs,
                    "my_upcoming_rides": my_upcoming_rides}
                  )


def club_home(request, club_id):
    event_occurences = EventOccurence.objects.filter(event__club__pk=club_id)
    return render(request=request,
                  template_name="groupridesapp/club_home.html",
                  context={"event_occurences": event_occurences})

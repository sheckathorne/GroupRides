import datetime

from django.shortcuts import render, get_object_or_404
from .models import Club, EventOccurence, EventOccurenceMember, ClubMembership
from django.db.models import Q
from .forms import DeleteRideRegistrationForm, CreateRideRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect


def days_from_today(n):
    return datetime.date.today() + datetime.timedelta(days=n)


@login_required(login_url='/login')
def homepage(request):
    days_in_the_future = days_from_today(11)

    my_upcoming_rides = EventOccurenceMember.objects.filter(
        user=request.user,
        event_occurence__ride_date__lte=days_in_the_future,
        event_occurence__ride_date__gte=datetime.date.today()
    ).order_by('event_occurence__ride_date')

    my_clubs = Club.objects.filter(
        clubmembership__user=request.user
    )

    return render(request=request,
                  template_name="groupridesapp/home.html",
                  context={
                    "my_clubs": my_clubs,
                    "my_upcoming_rides": my_upcoming_rides,
                    "available_rides": available_rides,
                    "user": request.user
                  })


@login_required(login_url='/login')
def my_rides(request):
    days_in_the_future = days_from_today(11)

    my_upcoming_rides = EventOccurenceMember.objects.filter(
        user=request.user,
        event_occurence__ride_date__lte=days_in_the_future,
        event_occurence__ride_date__gte=datetime.date.today()
    ).order_by('event_occurence__ride_date')

    return render(request=request,
                  template_name="groupridesapp/rides/my_rides.html",
                  context={
                    "my_upcoming_rides": my_upcoming_rides,
                    "user": request.user
                  })


@login_required(login_url='/login')
def available_rides(request):
    days_in_the_future = days_from_today(11)

    available_rides_queryset = EventOccurence.objects.exclude(
        # Exclude rides which I'm already subscribed to
        pk__in=EventOccurenceMember.objects.filter(
            user=request.user
        ).values('event_occurence')
    ).filter(
        # Rides where I have joined the club regardless of membership level
        privacy__lte=EventOccurence.EventMemberType.Open,
        club__in=ClubMembership.objects.filter(
            user=request.user).values('club')
    ).filter(
        ride_date__lte=days_in_the_future,
        ride_date__gte=datetime.date.today()
    ).order_by('ride_date')

    return render(request=request,
                  template_name="groupridesapp/rides/available_rides.html",
                  context={
                    "available_rides": available_rides_queryset,
                    "user": request.user
                  })


@login_required(login_url='/login')
def club_home(request, club_id):
    event_occurences = EventOccurence.objects.filter(event__club__pk=club_id)

    return render(request=request,
                  template_name="groupridesapp/club_home.html",
                  context={"event_occurences": event_occurences})


@login_required(login_url='/login')
def delete_ride_reigstration(request, event_occurence_id):
    event_occurences = EventOccurenceMember.objects.filter(
        Q(event_occurence__ride_date__gte=datetime.date.today()),
        Q(event_occurence__created_by=request.user) | Q(user=request.user)
    )

    registration_to_delete = get_object_or_404(event_occurences, id=event_occurence_id)

    if request.method == 'POST':
        form = DeleteRideRegistrationForm(request.POST, instance=registration_to_delete)

        if form.is_valid():
            registration_to_delete.delete()
            messages.error(request, "Successfully unregistered from ride.")
            return HttpResponseRedirect("/")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

            form = DeleteRideRegistrationForm(instance=registration_to_delete)

        template_vars = {'form': form}

        return render(
            request=request,
            context=template_vars
        )


@login_required(login_url='/login')
def create_ride_registration(request, event_occurence_id):
    if request.method == 'POST':
        event_occurence = get_object_or_404(EventOccurence, id=event_occurence_id)

        data = {
            'user': request.user,
            'event_occurence': event_occurence,
            'role': 2
        }

        EventOccurenceMember.objects.create(**data)
        messages.success(request, "Successfully registered to ride.")
        return HttpResponseRedirect("/")


@login_required(login_url='/login')
def ride_attendees(request, event_occurence_member_id):
    event_occurence = get_object_or_404(EventOccurenceMember, id=event_occurence_member_id).event_occurence

    event_members = EventOccurenceMember.objects.filter(
        event_occurence=event_occurence
    ).order_by('role')

    return render(request=request,
                  template_name="groupridesapp/rides/ride_attendees.html",
                  context={
                      "event_occurence": event_occurence,
                      "event_members": event_members})

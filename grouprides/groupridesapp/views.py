import datetime

from django.shortcuts import render, get_object_or_404
from .models import Club, EventOccurence, EventOccurenceMember, ClubMembership
from django.db.models import Q, Count
from .forms import DeleteRideRegistrationForm, CreateRideRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect


def days_from_today(n):
    return datetime.date.today() + datetime.timedelta(days=n)


def club_total_from(qs, club_name):
    return qs.get(club__name=club_name)['total']


def club_ride_count(qs, club_name):
    return 0 if not qs.exists() else club_total_from(qs, club_name)


def gather_available_rides(user):
    days_in_the_future = days_from_today(11)

    return EventOccurence.objects.exclude(
        # Exclude rides which I'm already subscribed to
        pk__in=EventOccurenceMember.objects.filter(
            user=user
        ).values('event_occurence')
    ).filter(
        # Rides where I have joined the club regardless of membership level
        privacy__lte=EventOccurence.EventMemberType.Open,
        club__in=ClubMembership.objects.filter(
            user=user).values('club')
    ).filter(
        ride_date__lte=days_in_the_future,
        ride_date__gte=datetime.date.today()
    )


@login_required(login_url='/login')
def homepage(request):
    my_clubs = Club.objects.filter(
        clubmembership__user=request.user
    )

    return render(request=request,
                  template_name="groupridesapp/home.html",
                  context={
                      "my_clubs": my_clubs,
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
def available_rides_clubs(request):
    arq = gather_available_rides(user=request.user)

    available_rides_club = arq.values('club__name', 'club__id', 'club__slug').annotate(total=Count('club__id'))

    available_rides_A = (arq.filter(group_classification=EventOccurence.GroupClassification.A)
                         .values('club__name', 'club__id', 'club__slug')
                         .annotate(total=Count('club__id')))

    available_rides_B = (arq.filter(group_classification=EventOccurence.GroupClassification.B)
                         .values('club__name', 'club__id', 'club__slug')
                         .annotate(total=Count('club__id')))

    available_rides_C = (arq.filter(group_classification=EventOccurence.GroupClassification.C)
                         .values('club__name', 'club__id', 'club__slug')
                         .annotate(total=Count('club__id')))

    available_rides_D = (arq.filter(group_classification=EventOccurence.GroupClassification.D)
                         .values('club__name', 'club__id', 'club__slug')
                         .annotate(total=Count('club__id')))

    available_rides_N = (arq.filter(group_classification=EventOccurence.GroupClassification.N)
                         .values('club__name', 'club__id', 'club__slug')
                         .annotate(total=Count('club__id')))

    available_rides_NA = (arq.filter(group_classification=EventOccurence.GroupClassification.NA)
                          .values('club__name', 'club__id', 'club__slug')
                          .annotate(total=Count('club__id')))

    clubs = []
    for club in available_rides_club:

        club_name = club['club__name']
        new_club = {
            'name': club_name,
            'slug': club['club__slug'],
            'id': club['club__id'],
            'total': club['total'],
            'A': club_ride_count(available_rides_A, club_name),
            'B': club_ride_count(available_rides_B, club_name),
            'C': club_ride_count(available_rides_C, club_name),
            'D': club_ride_count(available_rides_D, club_name),
            'N': club_ride_count(available_rides_N, club_name),
            'NA': club_ride_count(available_rides_NA, club_name)
        }

        clubs.append(new_club)

    return render(request=request,
                  template_name="groupridesapp/rides/available_rides_clubs.html",
                  context={
                      "available_rides_clubs": clubs,
                      "user": request.user
                  })


@login_required(login_url='/login')
def available_rides(request, club_id, group_classification="", **kwargs):
    if len(group_classification) > 0:
        arq = gather_available_rides(user=request.user).filter(club=club_id).filter(group_classification=group_classification)
    else:
        arq = gather_available_rides(user=request.user).filter(club=club_id)

    available_rides_queryset = arq.order_by('ride_date')

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

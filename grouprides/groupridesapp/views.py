import datetime

from django.shortcuts import render, get_object_or_404, redirect
from .models import Club, EventOccurence, EventOccurenceMember, EventOccurenceMessage, EventOccurenceMessageVisit
from django.db.models import Q, F, Count, Value
from django.urls import reverse
from .forms import DeleteRideRegistrationForm
from .utils import days_from_today, club_ride_count, gather_available_rides
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from .decorators import user_is_ride_member
from django.utils import timezone


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

    # add comment counts for each ride in new property called comments {"total": 0, "new": 0}
    for ride in my_upcoming_rides:
        ride.comments = ride.num_comments(user=request.user)

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
    available_rides_club_groups = (arq
                                   .values('club__name', 'club__id', 'club__slug', 'group_classification')
                                   .annotate(total=Count('club__id')))

    clubs = []
    group_classification = EventOccurence.GroupClassification
    for club in available_rides_club:
        club_name = club['club__name']
        new_club = {
            'name': club_name,
            'slug': club['club__slug'],
            'id': club['club__id'],
            'total': club['total']
        }

        for gc in group_classification:
            new_club[gc.label] = club_ride_count(
                available_rides_club_groups.filter(
                    group_classification=gc.label),
                club_name)

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
        arq = (gather_available_rides(user=request.user)
               .filter(club=club_id)
               .filter(group_classification=group_classification))
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


@user_is_ride_member
def event_occurence_comments(request, event_occurence_id):
    event = EventOccurence.objects.get(pk=event_occurence_id)

    event_comments = (EventOccurenceMessage.objects
                      .filter(
                            event_occurence__id=event_occurence_id)
                      .order_by('create_date'))

    return render(request=request,
                  template_name="groupridesapp/rides/ride_comments.html",
                  context={
                    "event_comments": event_comments,
                    "event": event})


@login_required(login_url='/login')
def create_ride_registration(request, event_occurence_id):
    if request.method == "POST":
        event_occurence = get_object_or_404(EventOccurence, id=event_occurence_id)

        data = {
            'user': request.user,
            'event_occurence': event_occurence,
            'role': 2
        }

        EventOccurenceMember.objects.create(**data)
        messages.success(request, "Successfully registered to ride.")
        return HttpResponseRedirect(reverse('my_rides'))


@login_required(login_url='/login')
def event_occurence_comments_click(request, event_occurence_id):
    if request.method == "POST":
        event_occurence = get_object_or_404(EventOccurence, id=event_occurence_id)

        data = {
            'user': request.user,
            'event_occurence': event_occurence,
        }

        EventOccurenceMessageVisit.objects.update_or_create(**data, defaults={'last_visit': timezone.now()})
        return HttpResponseRedirect(reverse('ride_comments', args=(event_occurence_id,)))


@user_is_ride_member
def create_event_occurence_message(request, event_occurence_id):
    return redirect('/')

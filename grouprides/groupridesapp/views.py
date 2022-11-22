import datetime

from django.shortcuts import render, get_object_or_404
from .models import Club, EventOccurence, EventOccurenceMember, ClubMembership
from django.db.models import Q
from .forms import DeleteRideRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect


@login_required(login_url='/login')
def homepage(request):
    next_ten_days = datetime.date.today() + datetime.timedelta(days=11)

    my_upcoming_rides = EventOccurenceMember.objects.filter(
        user=request.user,
        event_occurence__ride_date__lte=next_ten_days,
        event_occurence__ride_date__gte=datetime.date.today()
    ).order_by('event_occurence__ride_date')

    available_rides = EventOccurence.objects.exclude(
        # Exclude rides which I'm already subscribed to
        pk__in=EventOccurenceMember.objects.filter(
            user=request.user
        )
    ).filter(
        # Club rides which are private and I am a member
        Q(
            Q(privacy=EventOccurence.EventMemberType.Members),
            Q(club__in=ClubMembership.objects.filter(
                user=request.user,
                membership_type__lte=3).values('club'))
        ) |
        # Club rides which are open, but I am not a member
        Q(
            Q(privacy=EventOccurence.EventMemberType.Members),
            Q(club__in=ClubMembership.objects.filter(
                user=request.user,
                membership_type__lte=4).values('club'))
        )
    ).filter(
        # only show rides in the available window
        ride_date__lte=next_ten_days,
        ride_date__gte=datetime.date.today()
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




@login_required
def delete_ride_reigstration(request, registration_id):
    event_occurences = EventOccurenceMember.objects.filter(
        Q(event_occurence__ride_date__gte=datetime.date.today()),
        Q(event_occurence__created_by=request.user) | Q(user=request.user)
    )

    registration_to_delete = get_object_or_404(event_occurences, id=registration_id)

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
            template_name='confirm_ride_deregistration.html',
            context=template_vars
        )


@login_required
def ride_attendees(request, event_occurence_member_id):
    event_occurence = get_object_or_404(EventOccurenceMember, id=event_occurence_member_id).event_occurence

    event_members = EventOccurenceMember.objects.filter(
        event_occurence=event_occurence
    ).order_by('role')

    return render(request=request,
                  template_name="groupridesapp/ride_attendees.html",
                  context={
                      "event_occurence": event_occurence,
                      "event_members": event_members})

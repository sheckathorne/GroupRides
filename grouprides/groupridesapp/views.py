import datetime
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.utils import IntegrityError

from .filters import RideFilter
from .models import Club, EventOccurence, EventOccurenceMember, \
    EventOccurenceMessage, EventOccurenceMessageVisit, Event, Route, ClubMembership, ClubMembershipRequest
from django.db.models import Q
from django.urls import reverse
from .forms import DeleteRideRegistrationForm, CreateEventOccurenceMessageForm, \
    CreateClubForm, CreateEventForm, CreateRouteForm, ClubMembershipForm
from .paginators import CustomPaginator
from .utils import days_from_today, gather_available_rides, get_filter_fields, \
    get_event_comments, get_members_by_type, \
    distinct_errors
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.utils.text import slugify


@login_required(login_url='/login')
def homepage(request):
    items = [str(x) for x in range(1, 21)]

    pagination = CustomPaginator(
        request,
        items,
        1,
        on_each_side=2,
        on_ends=1
    )

    return render(request=request,
                  template_name="groupridesapp/home.html",
                  context={
                      "pagination_items": pagination.html_list,
                      "display_items": pagination.item_list
                  })


@login_required(login_url='/login')
def my_clubs(request):
    clubs = ClubMembership.objects.filter(
        user=request.user
    ).order_by('membership_type')

    return render(request=request,
                  template_name="groupridesapp/clubs/my_clubs.html",
                  context={
                      "clubs": clubs,
                      "user": request.user
                  })


@login_required(login_url='/login')
def my_rides(request):
    TABLE_PREFIX = "event_occurence__"

    my_upcoming_rides = EventOccurenceMember.objects.filter(
        user=request.user,
        event_occurence__ride_date__lte=days_from_today(11),
        event_occurence__ride_date__gte=datetime.date.today()
    ).order_by('event_occurence__ride_date')

    f = RideFilter(
        request.GET,
        queryset=my_upcoming_rides,
        filter_fields=get_filter_fields(my_upcoming_rides, TABLE_PREFIX),
    )

    ride_queryset = f.qs.order_by(f"{TABLE_PREFIX}ride_date", f"{TABLE_PREFIX}ride_time")

    pagination = CustomPaginator(
        request,
        ride_queryset,
        4,
        on_each_side=2,
        on_ends=1
    )

    item_list = pagination.item_list

    for ride in item_list:
        ride.comments = ride.num_comments(user=request.user)

    return render(request=request,
                  template_name="groupridesapp/rides/my_rides.html",
                  context={
                      "form": f.form,
                      "pagination_items": pagination.html_list,
                      "my_upcoming_rides": item_list,
                      "user": request.user
                  })


@login_required(login_url='/login')
def available_rides(request):
    TABLE_PREFIX = ""

    arq = gather_available_rides(user=request.user)

    f = RideFilter(
        request.GET,
        queryset=arq,
        filter_fields=get_filter_fields(arq, TABLE_PREFIX)
    )

    ride_queryset = f.qs.order_by(f"{TABLE_PREFIX}ride_date", f"{TABLE_PREFIX}ride_time")

    pagination = CustomPaginator(
        request,
        ride_queryset,
        4,
        on_each_side=2,
        on_ends=1
    )

    return render(request=request,
                  template_name="groupridesapp/rides/available_rides.html",
                  context={
                      "form": f.form,
                      "pagination_items": pagination.html_list,
                      "event_occurences": pagination.item_list
                  })


@login_required(login_url='/login')
def delete_ride_registration(request, event_occurence_id):
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
            return HttpResponseRedirect(reverse('my_rides'))
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

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


class EventComments(TemplateView):
    def get(self, request, **kwargs):
        event_occurence_id = kwargs["event_occurence_id"]
        form = CreateEventOccurenceMessageForm()
        event = get_object_or_404(EventOccurence, id=event_occurence_id)
        event_comments = get_event_comments(occurence_id=event_occurence_id, order_by='create_date')

        pagination = CustomPaginator(
            request,
            event_comments,
            5,
            on_each_side=2,
            on_ends=1
        )

        return render(request=request,
                      template_name="groupridesapp/rides/ride_comments.html",
                      context={
                          "event_comments": pagination.item_list,
                          "pagination_items": pagination.html_list,
                          "event": event,
                          "form": form
                      })

    @staticmethod
    def post(request, **kwargs):
        event_occurence_id = kwargs["event_occurence_id"]
        event = EventOccurence.objects.get(pk=event_occurence_id)
        if request.method == 'POST':
            form_data = CreateEventOccurenceMessageForm(request.POST)
            if form_data.is_valid():
                data = {
                    'message': form_data['message'].value(),
                    'user': request.user,
                    'event_occurence': event
                }

                click_data = {
                    'user': request.user,
                    'event_occurence': event,
                }

                EventOccurenceMessage.objects.create(**data)
                EventOccurenceMessageVisit.objects.update_or_create(
                    **click_data,
                    defaults={'last_visit': timezone.now()})

                return HttpResponseRedirect(reverse('ride_comments', args=(event_occurence_id,)))
            else:
                messages.error(request, 'Comment cannot be blank.')

        return HttpResponseRedirect(reverse('ride_comments', args=(event_occurence_id,)))


class CreateClub(TemplateView):
    def get(self, request, **kwargs):
        form = CreateClubForm()
        return render(
            request=request,
            template_name="groupridesapp/clubs/create_club.html",
            context={"form": form}
        )

    @staticmethod
    def post(request):
        if request.method == 'POST':
            form = CreateClubForm(request.POST)
            if form.is_valid():
                user = request.user
                slug = slugify(form['name'].value())
                data = {
                    'name': form['name'].value(),
                    'web_url': form['web_url'].value(),
                    'logo_url': form['logo_url'].value(),
                    'zip_code': form['zip_code'].value(),
                    'private': form['private'].value(),
                    "created_by": user,
                    "slug": slug,
                }

                Club.objects.create(**data)
                return HttpResponseRedirect('/')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = CreateClubForm()

        return render(
            request=request,
            template_name="groupridesapp/clubs/create_club.html",
            context={'form': form}
        )


def get_user_routes(user):
    return Route.objects.filter(created_by=user)


def get_user_and_club_routes(user):
    return Route.objects.filter(
        Q(created_by=user) |
        Q(club__in=ClubMembership.objects.filter(
            user=user,
            membership_type__lte=ClubMembership.MemberType.RideLeader.value).values('club')
          )
    )


def get_user_clubs(user, member_type):
    return (Club.objects.filter(
        pk__in=ClubMembership.objects.filter(
            user=user, membership_type__lte=member_type.value)
        .values('club')))


class CreateEvent(TemplateView):
    def get(self, request, **kwargs):
        user_routes = get_user_and_club_routes(request.user)
        user_clubs = get_user_clubs(request.user, ClubMembership.MemberType.RideLeader)
        if not user_routes.exists():
            messages.warning(request, "Cannot create ride without any routes added. Please create a route first.")
            return HttpResponseRedirect('/')
        else:
            form = CreateEventForm(user_clubs, user_routes)

            return render(
                request=request,
                template_name="groupridesapp/events/create_event.html",
                context={"form": form}
            )

    @staticmethod
    def post(request):
        user_routes = get_user_and_club_routes(request.user)
        user_clubs = get_user_clubs(request.user, ClubMembership.MemberType.RideLeader)

        if request.method == 'POST':
            form = CreateEventForm(user_clubs, user_routes, request.POST)
            if form.is_valid():
                club = None if form['club'].value() == '' else Club.objects.get(pk=form['club'].value())
                data = {
                    'name': form['name'].value(),
                    'created_by': request.user,
                    'privacy': form['privacy'].value(),
                    'club': club,
                    'start_date': form['start_date'].value(),
                    'end_date': form['end_date'].value(),
                    'ride_time': form['ride_time'].value(),
                    'time_zone': form['time_zone'].value(),
                    'frequency': form['frequency'].value(),
                    'max_riders': form['max_riders'].value(),
                    'group_classification': form['group_classification'].value(),
                    'lower_pace_range': form['lower_pace_range'].value(),
                    'upper_pace_range': form['upper_pace_range'].value(),
                    'route': Route.objects.get(pk=form['route'].value()),
                    'weekdays': form.cleaned_data.get('weekdays')
                }

                Event.objects.create(**data)
                messages.success(request, 'Successfully created your ride!')
                return HttpResponseRedirect(reverse('my_rides'))
            else:
                errors = distinct_errors(form.errors.values())
                for error in errors:
                    messages.error(request, error)

        form = CreateEventForm(user_clubs, user_routes, request.POST)

        return render(
            request=request,
            template_name="groupridesapp/events/create_event.html",
            context={"form": form}
        )


class CreateRoute(TemplateView):
    def get(self, request, **kwargs):
        user_clubs = get_user_clubs(request.user, ClubMembership.MemberType.RouteContributor)
        form = CreateRouteForm(user_clubs)
        return render(
            request=request,
            template_name="groupridesapp/routes/create_route.html",
            context={"form": form}
        )

    @staticmethod
    def post(request):
        user_clubs = get_user_clubs(request.user, ClubMembership.MemberType.RouteContributor)
        if request.method == "POST":
            form = CreateRouteForm(user_clubs, request.POST)
            if form.is_valid():
                club = None if form['club'].value() == '' else Club.objects.get(pk=form['club'].value())
                data = {
                    "name": form["name"].value(),
                    "start_location_name": form["start_location_name"].value(),
                    "distance": form["distance"].value(),
                    "elevation": form["elevation"].value(),
                    "shared": form["shared"].value(),
                    "club": club
                }

                Route.objects.create(**data, created_by=request.user)
                messages.success(request, "Successfully created new route.")
                return HttpResponseRedirect("/")

            form = CreateRouteForm(user_clubs, request.POST)
            return render(
                request=request,
                template_name="groupridesapp/routes/create_route.html",
                context={"form": form}
            )


class ClubMemberManagement(TemplateView):
    def get(self, request, **kwargs):
        club_id = kwargs['club_id']
        slug = kwargs['_slug']
        tab_type = kwargs.get('tab_type', None)

        club = Club.objects.get(pk=club_id)

        aqs = ClubMembership.objects.filter(
            club=club_id
        ).order_by('membership_type', 'user__last_name', 'user__first_name')

        reqs = ClubMembershipRequest.objects.filter(
            club=club_id
        ).order_by('request_date')

        pending_count = ClubMembershipRequest.objects.filter(
            club=club_id,
            status=ClubMembershipRequest.RequestStatus.Pending
        ).count()

        members = get_members_by_type(tab_type, aqs)
        tab_classes = {'active': '', 'inactive': '', 'requests': '', tab_type: ' show active'}

        for member in members:
            print(member)

        return render(request=request,
                      template_name="groupridesapp/clubs/members/members_tabs.html",
                      context={
                          "members": members,
                          "reqs": reqs,
                          "pending_count": pending_count,
                          "user": request.user,
                          "slug": slug,
                          "club_id": club_id,
                          "club_name": club.name,
                          "tab_classes": tab_classes,
                          "tab_type": tab_type,
                      })

    @staticmethod
    def post(request, **kwargs):
        club_id = kwargs['club_id']
        slug = kwargs['_slug']
        membership_id = kwargs['membership_id']
        club_membership = get_object_or_404(ClubMembership, pk=membership_id)

        if request.method == "POST":
            form = ClubMembershipForm(request.POST, user=request.user, club_id=club_id, instance=club_membership)
            if form.is_valid():
                form.save()
                messages.success(request, "Successfully updated membership details")
                return redirect(reverse("club_member_management", kwargs={
                    '_slug': slug,
                    'club_id': club_id,
                    'tab_type': 'active'}))
            else:
                for errortype in form.errors.as_data()['__all__']:
                    for error in errortype:
                        messages.error(request, error)
                return redirect(reverse("club_member_management", kwargs={
                    '_slug': slug,
                    'club_id': club_id,
                    'tab_type': 'active'}))
        else:
            form = ClubMembershipForm(user=request.user, instance=club_membership)

        return render(
            request,
            reverse("club_member_management", kwargs={
                '_slug': slug,
                'club_id': club_id,
                'tab_type': 'active'}),
            {"form": form}
        )


def deactivate_membership(request, _slug, club_id, membership_id, tab_type):
    membership = get_object_or_404(ClubMembership, pk=membership_id)
    requestor_membership = ClubMembership.objects.get(
        club=club_id,
        user=request.user
    )

    requestor_role = requestor_membership.membership_type
    member_role = membership.membership_type
    creator_role_type = ClubMembership.MemberType.Creator.value

    if member_role == creator_role_type and requestor_role > creator_role_type:
        messages.error(request, "Only creators can modify a creator.")

        raise ValidationError(
            "Only creators can modify a creator."
        )
    else:
        membership.active = not membership.active
        membership.save()
        messages.success(request, "Changed active status!")

        response = HttpResponse()

        response["HX-Redirect"] = reverse("club_member_management", kwargs={
                '_slug': _slug,
                'club_id': club_id,
                'tab_type': tab_type})

        return response


def reject_membership_request(request, membership_request_id, **kwargs):
    membership_request = get_object_or_404(ClubMembershipRequest, pk=membership_request_id)

    membership_request.status = ClubMembershipRequest.RequestStatus.Denied
    membership_request.responder = request.user
    membership_request.response_date = timezone.now()

    membership_request.save()
    messages.success(request, "Successfully rejected the membership request.")

    return redirect(request.META['HTTP_REFERER'])


def create_club_member(request, _slug, club_id, membership_request_id):
    if request.method == "POST":
        form = ClubMembershipForm(
            request.POST,
            user=request.user,
            club_id=club_id,
            membership_request_id=membership_request_id
        )

        if form.is_valid():
            membership_request = ClubMembershipRequest.objects.get(pk=membership_request_id)
            club = Club.objects.get(pk=club_id)

            data = {
                "user": membership_request.user,
                "club": club,
                "membership_expires": form["membership_expires"].value(),
                "active": form["active"].value(),
                "membership_type": form["membership_type"].value(),
            }

            try:
                name = f"{membership_request.user.first_name} {membership_request.user.last_name}"
                ClubMembership.objects.create(**data)
            except IntegrityError:
                messages.error(request, f"Could not create club membership, {name} is already a member.")
            else:
                messages.success(request, f"Successfully added {name} to {club.name}.")

            return redirect(reverse("club_member_management", kwargs={
                '_slug': _slug,
                'club_id': club_id,
                'tab_type': 'active'}))

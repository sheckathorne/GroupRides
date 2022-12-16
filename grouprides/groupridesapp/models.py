import datetime
import pytz

from django.utils import timezone
from django.db import models
from users.models import CustomUser
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Count, F
from tinymce.models import HTMLField
from django.core.exceptions import ValidationError


def length_of_five(value):
    if len(value) != 5:
        raise ValidationError('Zip code should have a length of five')


def numeric_chars(value):
    if not value.isnumeric():
        raise ValidationError(f'{value} should be numbers only')


def six_months_from(start_date, end_date):
    if end_date > start_date + relativedelta(months=+6):
        raise ValidationError('End date must be within 6 months of start date')


def upper_greater_than_lower_pace(lower, upper):
    if lower > upper:
        raise ValidationError('Upper pace range should be greater than lower pace range')


def ride_is_full(max_riders, number_of_riders):
    if number_of_riders >= max_riders:
        raise ValidationError('Ride is full.')


def max_is_fewer_than_riders(max_riders, number_of_riders):
    if max_riders and number_of_riders and max_riders < number_of_riders:
        raise ValidationError('Cannot set max riders fewer than number of signed up riders')


def membership_is_expired(expiration_date, event_date):
    if event_date > expiration_date:
        raise ValidationError('Club membership expires before event date')


def not_member_of_club(membership_exists):
    if not membership_exists:
        raise ValidationError('Must be a club member to join this event')


class Club(models.Model):
    name = models.CharField("Name", max_length=255)
    web_url = models.CharField("Website", max_length=255)
    logo_url = models.CharField("Logo URL", max_length=500)
    zip_code = models.CharField("Zip Code", max_length=5, validators=[numeric_chars, length_of_five])
    private = models.BooleanField("Private")
    create_date = models.DateField("Date Created", auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if created:
            ClubMembership.objects.create(
                user=self.created_by,
                club=self,
                active=True,
                membership_expires=datetime.datetime(year=9999, month=12, day=31),
                membership_type=ClubMembership.MemberType.Creator
            )

    def __str__(self):
        return self.name


class ClubMembership(models.Model):
    class MemberType(models.IntegerChoices):
        Creator = (1, "Creator")
        Admin = (2, "Admin")
        RideLeader = (3, "Ride Leader")
        RouteContributor = (4, "Route Contributor")
        PaidMember = (5, "Paid Member")
        UnpaidMember = (6, "Unpaid Member")
        NonMember = (7, 'Non-Member')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    create_date = models.DateField("Date Joined", auto_now_add=True)
    membership_expires = models.DateField("Membership Expires")
    active = models.BooleanField("Active", default=True)
    membership_type = models.IntegerField("Membership Type", choices=MemberType.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'club'], name='One user membership per club')
        ]

    def is_expired(self):
        now = timezone.now().date()
        return self.membership_expires < now

    def is_inactive(self):
        return not self.active

    @property
    def level(self):
        return ClubMembership.MemberType(self.membership_type).label

    @property
    def expired(self):
        now = timezone.now().date()
        return self.membership_expires < now

    @property
    def inactive(self):
        return not self.active

    @property
    def user_can_manage_club(self):
        return self.membership_type <= ClubMembership.MemberType.Admin.value

    @property
    def membership_type_label(self):
        return ClubMembership.MemberType(self.membership_type).label

    def __str__(self):
        return (
                self.club.name + " - " +
                self.user.last_name + ", " +
                self.user.first_name + " - " + ClubMembership.MemberType(self.membership_type).label
        )


class ClubMembershipRequest(models.Model):
    class RequestStatus(models.IntegerChoices):
        Pending = (1, 'Pending')
        Approved = (2, 'Approved')
        Denied = (3, 'Denied')

    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name="request_user", on_delete=models.CASCADE)
    responder = models.ForeignKey(CustomUser, related_name="response_user", blank=True, null=True, on_delete=models.CASCADE)
    request_date = models.DateTimeField("Request Date", auto_now_add=True)
    response_date = models.DateTimeField("Response Date", blank=True, null=True)
    status = models.IntegerField("Request Status", choices=RequestStatus.choices,
                                 default=RequestStatus.Pending)

    @property
    def status_label(self):
        return ClubMembershipRequest.RequestStatus(self.status).label

    def __str__(self):
        return f"{self.user.last_name}, {self.user.first_name} to join {self.club.name}"


class Route(models.Model):
    name = models.CharField("Route Name", max_length=240)
    start_location_name = models.CharField("Start Location", max_length=240)
    url = models.CharField("Route URL", max_length=255)
    distance = models.DecimalField("Distance", max_digits=7, decimal_places=2)
    elevation = models.IntegerField("Elevation")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shared = models.BooleanField("Share With Club", default=False)
    club = models.ForeignKey(Club, blank=True, null=True, on_delete=models.CASCADE)
    date_created = models.DateField("Date Created", auto_now_add=True)

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if created:
            UserRoute.objects.create(
                user=self.created_by,
                route=self
            )

    def __str__(self):
        return f"{self.name}, by {self.created_by.first_name} {self.created_by.last_name} - {self.distance} miles"


class Event(models.Model):
    TIMEZONE_CHOICES = zip(pytz.all_timezones, pytz.all_timezones)

    class RecurrenceFrequency(models.IntegerChoices):
        Zero = (0, "None")
        Daily = (1, "Daily")
        Weekly = (7, "Weekly")
        Biweekly = (14, "Bi-Weekly")

    class GroupClassification(models.TextChoices):
        A = ("A", "A")
        B = ("B", "B")
        C = ("C", "C")
        D = ("D", "D")
        N = ("N", "Novice")
        NA = ("NA", "None")

    class MemberType(models.IntegerChoices):
        Creator = (1, "Creator")
        Admin = (2, "Admin")
        RideLeader = (3, "Ride Leader")
        RouteContributor = (4, "Route Contributor")
        PaidMember = (5, "Paid Member")
        UnpaidMember = (6, "Unpaid Member")
        NonMember = (7, 'Non-Member')

    class EventMemberType(models.IntegerChoices):
        Members = (ClubMembership.MemberType.PaidMember.value, "Current Members")
        Open = (ClubMembership.MemberType.NonMember.value, "Open")

    name = models.CharField("Event Name", max_length=100)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    privacy = models.IntegerField("Privacy", choices=EventMemberType.choices)
    club = models.ForeignKey(Club, on_delete=models.CASCADE,
                             blank=True, null=True, help_text="Only required if ride is private")
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")
    ride_time = models.TimeField("Ride Time")
    time_zone = models.CharField("Time Zone", default="America/Chicago", choices=TIMEZONE_CHOICES, max_length=100)
    frequency = models.IntegerField("Recurrence", choices=RecurrenceFrequency.choices)
    max_riders = models.PositiveIntegerField("Max Riders")
    is_canceled = models.BooleanField("Canceled", default=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    group_classification = models.CharField("Classification", choices=GroupClassification.choices, max_length=2)
    lower_pace_range = models.PositiveIntegerField("Lower Pace Range")
    upper_pace_range = models.PositiveIntegerField("Upper Pace Range")

    def __str__(self):
        return self.name

    def clean(self, *args, **kwargs):
        six_months_from(self.start_date, self.end_date)
        upper_greater_than_lower_pace(self.lower_pace_range, self.upper_pace_range)

    def save(self, *args, **kwargs):
        created = self.pk is None
        self.full_clean()
        super(Event, self).save(*args, **kwargs)
        if created:
            if self.frequency == 0:
                EventOccurence.objects.create(
                    event=self,
                    occurence_name=self.name,
                    created_by=self.created_by,
                    privacy=self.privacy,
                    club=self.club,
                    ride_date=self.start_date + datetime.timedelta(days=0),
                    ride_time=self.ride_time,
                    time_zone=self.time_zone,
                    max_riders=self.max_riders,
                    is_canceled=self.is_canceled,
                    route=self.route,
                    group_classification=self.group_classification,
                    lower_pace_range=self.lower_pace_range,
                    upper_pace_range=self.upper_pace_range
                )
            else:
                for i in range(0, (self.end_date - self.start_date).days + 1, self.frequency):
                    EventOccurence.objects.create(
                        event=self,
                        occurence_name=self.name,
                        created_by=self.created_by,
                        privacy=self.privacy,
                        club=self.club,
                        ride_date=self.start_date + datetime.timedelta(days=i),
                        ride_time=self.ride_time,
                        time_zone=self.time_zone,
                        max_riders=self.max_riders,
                        is_canceled=self.is_canceled,
                        route=self.route,
                        group_classification=self.group_classification,
                        lower_pace_range=self.lower_pace_range,
                        upper_pace_range=self.upper_pace_range
                    )


class EventOccurence(models.Model):
    TIMEZONE_CHOICES = zip(pytz.all_timezones, pytz.all_timezones)

    class GroupClassification(models.TextChoices):
        A = ("A", "A")
        B = ("B", "B")
        C = ("C", "C")
        D = ("D", "D")
        N = ("N", "Novice")
        NA = ("NA", "None")

    class TimezoneChoices(models.TextChoices):
        zip(pytz.all_timezones, pytz.all_timezones)

    class EventMemberType(models.IntegerChoices):
        Members = (Event.MemberType.PaidMember.value, "Current Members")
        Open = (Event.MemberType.NonMember.value, "Open")

    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.CASCADE)
    occurence_name = models.CharField("Event Name", max_length=100)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    privacy = models.IntegerField("Privacy", choices=EventMemberType.choices)
    club = models.ForeignKey(Club, null=True, blank=True,
                             help_text="Only required if private is selected", on_delete=models.CASCADE)
    ride_date = models.DateField("Ride Date")
    ride_time = models.TimeField("Ride Time")
    time_zone = models.CharField("Time Zone", default="America/Chicago", choices=TIMEZONE_CHOICES, max_length=100)
    max_riders = models.PositiveIntegerField("Max Riders")
    is_canceled = models.BooleanField("Canceled", default=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    group_classification = models.CharField("Classification", choices=GroupClassification.choices, max_length=2)
    lower_pace_range = models.PositiveIntegerField("Lower Pace Range")
    upper_pace_range = models.PositiveIntegerField("Upper Pace Range")

    @property
    def ride_leader_users(self):
        leaders = EventOccurenceMember.objects.filter(
            event_occurence=self,
            role=EventOccurenceMember.RoleType.Leader
        )

        return list(leaders)

    @property
    def time_until_ride(self):
        tz = pytz.timezone(self.time_zone)

        ride_datetime = datetime.datetime.combine(self.ride_date, self.ride_time)
        aware_ride_datetime = tz.localize(ride_datetime)
        current_datetime = datetime.datetime.now(tz)
        rd = relativedelta(aware_ride_datetime, current_datetime)

        time_diff = (
            f"{abs(rd.days)} day{'s'[:abs(rd.days) ^ 1]} and {abs(rd.hours)} hour{'s'[:abs(rd.hours) ^ 1]}" if abs(
                rd.days) > 0 else
            f"{abs(rd.hours)} hour{'s'[:abs(rd.hours) ^ 1]}")

        if rd.days + rd.hours == 0:
            return "Now"
        elif rd.days + rd.hours > 0:
            return f"(in {time_diff})"
        else:
            return f"({time_diff} ago)"

    @property
    def is_private(self):
        return self.privacy == self.EventMemberType.Members

    @property
    def ride_leader_name(self):
        leader_name = ""

        if len(self.ride_leader_users) == 1:
            leader = self.ride_leader_users[0].user
            leader_name = f"{leader.first_name} {leader.last_name}"
        elif len(self.ride_leader_users) > 1:
            leader = self.ride_leader_users[0].user
            leader_name = f"{leader.first_name} {leader.last_name}"
            for i in range(1, len(self.ride_leader_users)):
                leader_name = leader_name + f" + {leader.first_name} {leader.last_name}"

        return leader_name

    def can_be_joined_by(self, user):
        return EventOccurence.objects.filter(
            Q(
                Q(privacy=EventOccurence.EventMemberType.Members),
                Q(club__in=ClubMembership.objects.filter(
                    user=user,
                    membership_type__lte=EventOccurence.EventMemberType.Members.value).values('club'))
            ) |
            Q(
                Q(privacy=EventOccurence.EventMemberType.Open),
                Q(club__in=ClubMembership.objects.filter(
                    user=user,
                    membership_type__lte=EventOccurence.EventMemberType.Open.value).values('club'))
            )).filter(pk=self.pk).exists()

    @property
    def number_of_riders(self):
        return EventOccurenceMember.objects.filter(event_occurence__pk=self.pk).count()

    @property
    def percentage_full(self):
        return (self.number_of_riders / float(self.max_riders)) * 100

    @property
    def nearly_full(self):
        open_slots = self.max_riders - self.number_of_riders
        nearly_full = ((
                               self.max_riders >= 30 and self.percentage_full >= 90) or (
                               30 > self.max_riders >= 15 and self.percentage_full >= 80) or (
                               self.max_riders < 15 and self.percentage_full >= 70) or (
                               open_slots <= 2
                       ))
        return nearly_full

    @property
    def progress_bar_class(self):
        if self.max_riders == self.number_of_riders:
            return "progress-bar bg-danger"
        elif self.nearly_full:
            return "progress-bar bg-warning"
        else:
            return "progress-bar bg-success"

    @property
    def group_classification_name(self):
        return EventOccurence.GroupClassification(self.group_classification).label

    def clean(self):
        max_is_fewer_than_riders(self.max_riders, self.number_of_riders)

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if created:
            EventOccurenceMember.objects.create(
                event_occurence=self,
                user=self.created_by,
                role=1
            )

    def __str__(self):
        return self.occurence_name + " - " + self.ride_date.strftime("%b %d %Y")


class EventOccurenceMember(models.Model):
    class Meta:
        constraints = [models.UniqueConstraint(fields=['event_occurence', 'user'], name='unique_event_user')]

    class RoleType(models.IntegerChoices):
        Leader = (1, "Ride Leader")
        Rider = (2, "Rider")

    event_occurence = models.ForeignKey(EventOccurence, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    role = models.IntegerField("Role", choices=RoleType.choices, default=2)

    def num_comments(self, user):
        ride_id = self.event_occurence.id

        last_comment_visit_ride = (EventOccurenceMessageVisit.objects.filter(
            user=user
        ).order_by(
            'event_occurence', '-last_visit'
        ).values(
            'event_occurence_id', 'last_visit'
        ).distinct(
            'event_occurence'
        ).filter(
            event_occurence_id=ride_id))

        last_visit = (
            datetime.datetime(1900, 1, 1, tzinfo=timezone.utc) if not last_comment_visit_ride.exists()
            else last_comment_visit_ride.get(event_occurence_id=ride_id)["last_visit"])

        new_messages = (EventOccurenceMessage.objects.filter(
            event_occurence=ride_id,
            create_date__gte=last_visit
        ).values(
            'event_occurence'
        ).annotate(
            total=Count('event_occurence')))

        total_messages = EventOccurenceMessage.objects.filter(
            event_occurence__id=self.event_occurence.id
        ).values(
            'event_occurence__id'
        ).annotate(
            total=Count('event_occurence__id'))

        total_message_count = (
            0 if not total_messages.exists()
            else total_messages.get(event_occurence_id=ride_id)["total"])

        new_message_count = (
            0 if not new_messages.exists()
            else new_messages.get(event_occurence_id=ride_id)["total"])

        return {
            "total": total_message_count,
            "new": new_message_count
        }

    @property
    def is_ride_leader(self):
        return self.role == self.RoleType.Leader

    @property
    def is_private(self):
        return self.event_occurence.privacy == self.event_occurence.EventMemberType.Members

    def clean(self, *args, **kwargs):
        if self.event_occurence is not None:
            ride_is_full(self.event_occurence.max_riders, self.event_occurence.number_of_riders)

            # prevent non-members from joining members-only ride
            if EventOccurence.EventMemberType(self.event_occurence.privacy) is self.event_occurence.EventMemberType.Members:
                occurence_club = self.event_occurence.club
                club_membership_exists = ClubMembership.objects.filter(user=self.user, club=occurence_club).exists()
                not_member_of_club(club_membership_exists)

                membership = ClubMembership.objects.get(user=self.user, club=occurence_club)
                expiration_date = membership.membership_expires
                membership_is_expired(expiration_date, self.event_occurence.ride_date)

    def __str__(self):
        role = EventOccurenceMember.RoleType(self.role).label
        ride_date = self.event_occurence.ride_date.strftime("%b %d %Y")
        first_name = self.user.first_name
        last_name = self.user.last_name
        event_name = self.event_occurence.occurence_name
        return f"{event_name} - {ride_date} - {last_name}, {first_name} - {role}"


class EventOccurenceMessage(models.Model):
    event_occurence = models.ForeignKey(EventOccurence, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = HTMLField(blank=False)
    create_date = models.DateTimeField("Date Created", auto_now_add=True)

    @property
    def time_since_message(self):
        tz = pytz.timezone(self.event_occurence.time_zone)

        current_datetime = datetime.datetime.now(tz)
        rd = relativedelta(self.create_date, current_datetime)

        datetime_string = self.create_date.strftime("%-m/%-d/%Y - %I:%M%p")
        mins_since_comment = abs(rd.hours) * 60 + abs(rd.minutes)
        TWENTY_THREE_HOURS_FIFTY_NINE_MINUTES = 1439

        if mins_since_comment > TWENTY_THREE_HOURS_FIFTY_NINE_MINUTES:
            return f"{datetime_string}"
        elif mins_since_comment > 60:
            return f"{abs(rd.hours)} hour{'s'[:abs(rd.hours) ^ 1]} ago"
        elif mins_since_comment == 0:
            return "just now"
        else:
            return f"{abs(rd.minutes)} minute{'s'[:abs(rd.minutes) ^ 1]} ago"

    def __str__(self):
        first_name = self.user.first_name
        last_name = self.user.last_name
        create_date_string = self.create_date.strftime("%-m/%-d/%Y - %I:%M%p")
        return f"{first_name} {last_name} - {create_date_string}"


class EventOccurenceMessageVisit(models.Model):
    event_occurence = models.ForeignKey(EventOccurence, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    last_visit = models.DateTimeField("Date Created", auto_now_add=True)

    def __str__(self):
        last_visit_string = self.last_visit.strftime("%-m/%-d/%Y - %I:%M%p")
        return f"{self.event_occurence.occurence_name} - {last_visit_string}"


class UserRoute(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.route.name} for profile {self.user} by {self.route.created_by}"

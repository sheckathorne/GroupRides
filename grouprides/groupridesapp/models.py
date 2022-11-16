import datetime
import pytz

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser
from dateutil.relativedelta import relativedelta

# Validators


def length_of_five(value):
    if len(value) != 5:
        raise ValidationError('Zip code should have a length of five')


def numeric_chars(value):
    if not value.isnumeric():
        raise ValidationError(f'{value} should be numbers only')


def six_months_from(start_date, end_date):
    if end_date > start_date + relativedelta(months=+6):
        raise ValidationError('End date must be within 6 months of start date')


class EventMemberType(models.IntegerChoices):
    Members = (1, "Current Members")
    Open = (2, "Open")


class MemberType(models.IntegerChoices):
    Creator = (1, "Creator")
    Admin = (2, "Admin")
    Member = (3, "Member")
    NonMember = (4, "Non-Member")


TIMEZONE_CHOICES = zip(pytz.all_timezones, pytz.all_timezones)


class Club(models.Model):
    name = models.CharField("Name", max_length=255)
    web_url = models.CharField("Website", max_length=255)
    logo_url = models.CharField("Logo URL", max_length=255)
    zip_code = models.CharField("Zip Code", max_length=5, validators=[numeric_chars, length_of_five])
    private = models.BooleanField("Private")
    create_date = models.DateField("Date Created", auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

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


class Route(models.Model):
    name = models.CharField("Route Name", max_length=240)
    route_url = models.CharField("Route URL", max_length=255)
    distance = models.DecimalField("Distance", max_digits=7, decimal_places=2)
    elevation = models.IntegerField("Elevation")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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
        return self.name


class Event(models.Model):
    class RecurrenceFrequency(models.IntegerChoices):
        Zero = (0, "None")
        Daily = (1, "Daily")
        Weekly = (7, "Weekly")
        Biweekly = (14, "Bi-Weekly")

    name = models.CharField("Event Name", max_length=100)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    privacy = models.IntegerField("Privacy", choices=EventMemberType.choices)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")
    ride_time = models.TimeField("Ride Time")
    time_zone = models.CharField("Time Zone", default="America/Chicago", choices=TIMEZONE_CHOICES, max_length=100)
    frequency = models.IntegerField("Recurrence", choices=RecurrenceFrequency.choices)
    is_canceled = models.BooleanField("Canceled", default=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def clean(self,*args,**kwargs):
        six_months_from(self.start_date, self.end_date)

    def save(self, *args, **kwargs):
        created = self.pk is None
        self.full_clean()
        super(Event, self).save(*args, **kwargs)
        if created:
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
                    is_canceled=self.is_canceled,
                    route=self.route
                )


class EventOccurence(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    occurence_name = models.CharField("Event Name", max_length=100)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    privacy = models.IntegerField("Privacy", choices=MemberType.choices)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    ride_date = models.DateField("Ride Date")
    ride_time = models.TimeField("Ride Time")
    time_zone = models.CharField("Time Zone", default="America/Chicago", choices=TIMEZONE_CHOICES, max_length=100)
    is_canceled = models.BooleanField("Canceled", default=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)

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
    class RoleType(models.IntegerChoices):
        Leader = (1, "Ride Leader")
        Rider = (2, "Rider")

    event_occurence = models.ForeignKey(EventOccurence, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.IntegerField("Role", choices=RoleType.choices, default=2)

    @property
    def ride_leader_name(self):
        leader = EventOccurenceMember.objects.get(
            event_occurence=self.event_occurence,
            role=EventOccurenceMember.RoleType.Leader
        )

        leader_name = f"{leader.user.first_name} {leader.user.last_name}"
        return leader_name

    def __str__(self):
        role = EventOccurenceMember.RoleType(self.role).label
        ride_date = self.event_occurence.ride_date.strftime("%b %d %Y")
        first_name = self.user.first_name
        last_name = self.user.last_name
        event_name = self.event_occurence.event.name
        return f"{event_name} - {ride_date} - {last_name}, {first_name} - {role}"


class EventOccurenceMessage(models.Model):
    event_occurence_member = models.ForeignKey(EventOccurenceMember, on_delete=models.CASCADE)
    message = models.CharField("Message", max_length=255)

    def __str__(self):
        first_name = self.event_occurence_member.user.first_name
        last_name = self.event_occurence_member.user.last_name
        message = self.message
        return f"{first_name} {last_name} - {message}"


class UserRoute(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.route.name} for profile {self.user} by {self.route.created_by}"


class ClubMembership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    create_date = models.DateField("Date Joined", auto_now_add=True)
    membership_expires = models.DateField("Membership Expires")
    active = models.BooleanField("Active", default=True)
    membership_type = models.IntegerField("Membership Type", choices=MemberType.choices)

    def is_expired(self):
        now = timezone.now()
        return self.membership_expires < now

    def is_inactive(self):
        return not self.active

    def __str__(self):
        return (
            self.club.name + " - " +
            self.user.last_name + ", " +
            self.user.first_name + " - " + MemberType(self.membership_type).label
        )

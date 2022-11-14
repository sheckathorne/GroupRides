import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from users.models import CustomUser


def length_of_five(value):
    if len(value) != 5:
        raise ValidationError('Zip code should have a length of five')


def numeric_chars(value):
    if not value.isnumeric():
        raise ValidationError(f'{value} should be numbers only')


class Club(models.Model):
    name = models.CharField("Name", max_length=255)
    web_url = models.CharField("Website", max_length=255)
    logo_url = models.CharField("Logo URL", max_length=255)
    zip_code = models.CharField("Zip Code", max_length=5, validators=[numeric_chars, length_of_five])
    private = models.BooleanField("Private")
    create_date = models.DateField("Date Created", auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # When new Group is created, the user creating it has a new Group Membership object created
    # with no expiration date
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

    def __str__(self):
        return self.name


class ClubMembership(models.Model):
    class MemberType(models.TextChoices):
        Creator = ("1", "Creator")
        Admin = ("2", "Admin")
        Member = ("3", "Member")
        NonMember = ("4", "Non-Member")

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    create_date = models.DateField("Date Joined", auto_now_add=True)
    membership_expires = models.DateField("Membership Expires")
    active = models.BooleanField("Active", default=True)
    membership_type = models.CharField("Membership Type", choices=MemberType.choices, max_length=255)

    def is_expired(self):
        now = timezone.now()
        return self.membership_expires < now

    def is_inactive(self):
        return not self.active

    def __str__(self):
        return (
            self.club.name + " - " +
            self.user.last_name + ", " +
            self.user.first_name + " - " + ClubMembership.MemberType(self.membership_type).label
        )


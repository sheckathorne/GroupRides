from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


def length_of_five(value):
    if len(value) != 5:
        raise ValidationError('Zip code should have a length of five')


def numeric_chars(value):
    if not value.isnumeric():
        raise ValidationError(f'{value} should be numbers only')


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(name="First Name", max_length=50)
    last_name = models.CharField(name="Last Name", max_length=100)
    address = models.CharField("Address", max_length=40)
    zip_code = models.CharField("Zip Code", max_length=5, validators=[numeric_chars, length_of_five])

    def __str__(self):
        return self.username

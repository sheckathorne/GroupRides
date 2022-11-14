import datetime
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from .models import Club, ClubMembership
from users.models import CustomUser


def create_user(**kwargs):
    user_name = kwargs['user_name'] if 'user_name' in kwargs else 'username'
    email_address = kwargs['email_address'] if 'email_address' in kwargs else 'test.email@gmail.com'
    zip_code = kwargs['zip_code'] if 'zip_code' in kwargs else '12345'
    return CustomUser.objects.create(username=user_name, email=email_address, zip_code=zip_code)


def create_group(**kwargs):
    zip_code = kwargs['zip_code'] if 'zip_code' in kwargs else '12345'
    user = kwargs['user'] if 'user' in kwargs else create_user()

    return Club.objects.create(
        name="Group name",
        web_url="Web URL",
        logo_url="Logo URL",
        zip_code=zip_code,
        private=True,
        created_by=user
    )


class UserModelTests(TestCase):
    def test_zip_code_is_numeric_length_five(self):
        user = create_user(zip_code="12345")
        self.assertIsInstance(user, CustomUser)

    def test_zip_code_is_less_than_five_digits(self):
        user = create_user(zip_code="1234")
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_zip_code_is_more_than_five_digits(self):
        user = create_user(zip_code="123456")
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_zip_code_is_not_numeric(self):
        user = create_user(zip_code="AAAAA")
        with self.assertRaises(ValidationError):
            user.full_clean()


class GroupModelTests(TestCase):
    def test_zip_code_is_numeric_length_five(self):
        club = create_group(zip_code="12345")
        self.assertIsInstance(club, Club)

    def test_zip_code_is_less_than_five_digits(self):
        club = create_group(zip_code="1234")
        with self.assertRaises(ValidationError):
            club.full_clean()

    def test_zip_code_is_more_than_five_digits(self):
        club = create_group(zip_code="123456")
        with self.assertRaises(ValidationError):
            club.full_clean()

    def test_zip_code_is_not_numeric(self):
        club = create_group(zip_code="AAAAA")
        with self.assertRaises(ValidationError):
            club.full_clean()


class GroupMembershipModelTests(TestCase):
    def test_membership_is_inactive(self):
        user = create_user()
        create_group(user=user)
        club_membership = ClubMembership.objects.get(pk=1)
        club_membership.active = False
        print('membership:', club_membership.is_inactive())
        self.assertEquals(club_membership.is_inactive(), True)

    def test_membership_is_active(self):
        user = create_user()
        create_group(user=user)
        club_membership = ClubMembership.objects.get(pk=1)
        self.assertEquals(club_membership.is_inactive(), False)

    def test_membership_is_expired(self):
        user = create_user()
        create_group(user=user)
        club_membership = ClubMembership.objects.get(pk=1)
        club_membership.membership_expires = timezone.now() - datetime.timedelta(days=1)
        self.assertEquals(club_membership.is_expired(), True)

    def test_membership_is_not_expired(self):
        user = create_user()
        create_group(user=user)
        club_membership = ClubMembership.objects.get(pk=1)
        club_membership.membership_expires = timezone.now() + datetime.timedelta(days=1)
        self.assertEquals(club_membership.is_expired(), False)

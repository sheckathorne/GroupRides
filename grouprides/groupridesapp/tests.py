import datetime
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from .models import Rider, Group, GroupMembership
from django.contrib.auth.models import User


def create_user(**kwargs):
    user_name = kwargs['user_name'] if 'user_name' in kwargs else 'username'
    return User.objects.create(username=user_name, email="testuser@gmail.com")


def create_rider(**kwargs):
    user_name = kwargs['user_name'] if 'user_name' in kwargs else 'username'
    user = create_user(user_name=user_name)
    email_address = kwargs['email_address'] if 'email_address' in kwargs else 'test.email@gmail.com'
    zip_code = kwargs['zip_code'] if 'zip_code' in kwargs else '12345'

    return Rider.objects.create(
            first_name="Test",
            last_name="Rider",
            email_address=email_address,
            address="123 Main St",
            zip_code=zip_code,
            user=user,
        )


def create_group(**kwargs):
    zip_code = kwargs['zip_code'] if 'zip_code' in kwargs else '12345'
    rider = kwargs['rider'] if 'rider' in kwargs else create_rider()

    return Group.objects.create(
        name="Group name",
        web_url="Web URL",
        logo_url="Logo URL",
        zip_code=zip_code,
        private=True,
        created_by=rider
    )

class RiderModelTests(TestCase):
    def test_zip_code_is_numeric_length_five(self):
        rider = create_rider(zip_code="12345")
        self.assertIsInstance(rider, Rider)

    def test_zip_code_is_less_than_five_digits(self):
        rider = create_rider(zip_code="1234")
        with self.assertRaises(ValidationError):
            rider.full_clean()

    def test_zip_code_is_more_than_five_digits(self):
        rider = create_rider(zip_code="123456")
        with self.assertRaises(ValidationError):
            rider.full_clean()

    def test_zip_code_is_not_numeric(self):
        rider = create_rider(zip_code="AAAAA")
        with self.assertRaises(ValidationError):
            rider.full_clean()


class GroupModelTests(TestCase):
    def test_zip_code_is_numeric_length_five(self):
        group = create_group(zip_code="12345")
        self.assertIsInstance(group, Group)

    def test_zip_code_is_less_than_five_digits(self):
        group = create_group(zip_code="1234")
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_zip_code_is_more_than_five_digits(self):
        group = create_group(zip_code="123456")
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_zip_code_is_not_numeric(self):
        group = create_group(zip_code="AAAAA")
        with self.assertRaises(ValidationError):
            group.full_clean()


class GroupMembershipModelTests(TestCase):
    def test_membership_is_inactive(self):
        rider = create_rider()
        create_group(rider=rider)
        group_membership = GroupMembership.objects.get(pk=1)
        group_membership.active = False
        print('membership:', group_membership.is_inactive())
        self.assertEquals(group_membership.is_inactive(), True)

    def test_membership_is_active(self):
        rider = create_rider()
        create_group(rider=rider)
        group_membership = GroupMembership.objects.get(pk=1)
        self.assertEquals(group_membership.is_inactive(), False)

    def test_membership_is_expired(self):
        rider = create_rider()
        create_group(rider=rider)
        group_membership = GroupMembership.objects.get(pk=1)
        group_membership.membership_expires = timezone.now() - datetime.timedelta(days=1)
        self.assertEquals(group_membership.is_expired(), True)

    def test_membership_is_not_expired(self):
        rider = create_rider()
        create_group(rider=rider)
        group_membership = GroupMembership.objects.get(pk=1)
        group_membership.membership_expires = timezone.now() + datetime.timedelta(days=1)
        self.assertEquals(group_membership.is_expired(), False)

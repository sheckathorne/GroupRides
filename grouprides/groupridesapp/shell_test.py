# in shell run:
# exec(open('./groupridesapp/shell_test.py').read())

from users.models import CustomUser
from groupridesapp.models import Club, ClubMembership

user = CustomUser.objects.get(pk=1)
clubs = ClubMembership.objects.filter(
    user=user
)

print(clubs)
# in shell run:
# exec(open('./groupridesapp/shell_test.py').read())

from users.models import CustomUser
from groupridesapp.models import Club

user = CustomUser.objects.get(pk=1)
clubs = Club.objects.filter(
    clubmembership__user=user
)
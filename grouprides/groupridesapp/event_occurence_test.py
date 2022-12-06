# in shell run:
# exec(open('./groupridesapp/event_occurence_text.py).read())

from users.models import CustomUser
from groupridesapp.models import EventOccurence, EventOccurenceMember
from groupridesapp.views import days_from_today
import datetime

user = CustomUser.objects.get(pk=1)
days_in_the_future = days_from_today(11)

my_upcoming_rides = EventOccurenceMember.objects.select_related('event_occurence').filter(
    user=user,
    event_occurence__ride_date__lte=days_in_the_future,
    event_occurence__ride_date__gte=datetime.date.today()
).order_by('event_occurence__ride_date')

print(my_upcoming_rides)

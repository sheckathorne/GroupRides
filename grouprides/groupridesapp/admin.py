from django.contrib import admin
from .models import Club, Route, ClubMembership, UserRoute, Event, EventOccurence, EventOccurenceMember

# Register your models here.
admin.site.register(Route)
admin.site.register(Club)
admin.site.register(ClubMembership)
admin.site.register(UserRoute)
admin.site.register(Event)
admin.site.register(EventOccurence)
admin.site.register(EventOccurenceMember)


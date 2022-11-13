from django.contrib import admin
from .models import Rider, Club, Route, ClubMembership

# Register your models here.
admin.site.register(Rider)
admin.site.register(Route)
admin.site.register(Club)
admin.site.register(ClubMembership)


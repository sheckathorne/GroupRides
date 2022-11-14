from django.shortcuts import render
from django.http import HttpResponse
from .models import Club, Route, ClubMembership


def homepage(request):
    my_clubs = Club.objects.filter(clubmembership__user=request.user)
    return render(request=request,
                  template_name="groupridesapp/home.html",
                  context={"my_clubs": my_clubs}
                  )

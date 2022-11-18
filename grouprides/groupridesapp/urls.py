from django.urls import path
from django.contrib.auth import views as auth_views
from users import views as user_views
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path('clubs/<int:club_id>/', views.club_home, name="club_home"),
]

from django.urls import path
from django.contrib.auth import views as auth_views
from users import views as user_views
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path('clubs/<int:club_id>/', views.club_home, name="club_home"),
    path("register/", user_views.register, name="register"),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
]
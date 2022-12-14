from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm


def register(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Logged in as: {user.username}")
            return redirect('/')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegistrationForm()

    return render(
        request=request,
        template_name="users/register.html",
        context={"form": form}
        )


@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("homepage")


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Logged in successfully!")
                return redirect("homepage")
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        else:
            for key, error in list(form.errors.items()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, "You must pass the reCAPTCHA test")
                    continue
                messages.error(request, error)

    form = UserLoginForm()

    return render(
        request=request,
        template_name="users/login.html",
        context={'form': form}
    )

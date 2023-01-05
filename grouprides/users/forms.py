from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(help_text="Please enter a valid email address", required=True)

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field("first_name", css_class="shadow-lg", wrapper_class="mb-4"),
            Field("last_name", css_class="shadow-lg", wrapper_class="mb-4"),
            Field("username", css_class="shadow-lg", wrapper_class="mb-4"),
            Field("email", css_class="shadow-lg", wrapper_class="mb-4"),
            Field("password1", css_class="shadow-lg", wrapper_class="mb-4"),
            Field("password2", css_class="shadow-lg", wrapper_class="mb-4"),

            StrictButton("Sign Up", value="Register", type="submit",
                         css_class="w-full bg-white "
                                   "hover:bg-gradient-to-r from-sky-300 to-blue-200 "
                                   "text-gray-800 font-semibold py-2 px-4 border "
                                   "border-gray-400 rounded-lg shadow-lg mb-4")
        )

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field("username", css_class="shadow-lg", wrapper_class="mb-4", placeholder="Username or Email"),
            Field("password", css_class="shadow-lg", wrapper_class="mb-4", placeholder="Password"),
            Field("captcha", css_class="shadow-lg rounded-lg", wrapper_class="mb-4", placeholder="Enter Recaptcha"),
            StrictButton("Login", value="Login", type="submit",
                         css_class="w-full bg-white "
                                   "hover:bg-gradient-to-r from-sky-300 to-blue-200 "
                                   "text-gray-800 font-semibold py-2 px-4 border "
                                   "border-gray-400 rounded-lg shadow-lg")
        )

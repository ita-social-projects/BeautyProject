"""Module with forms for api application."""

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from api.models import CustomUser


class CustomUserCreationForm(forms.ModelForm):
    """A form for creating new users.

    Includes all the required fields, plus a repeated password.
    """
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation",
                                widget=forms.PasswordInput)

    class Meta:
        """Meta class where CustomUser model and fileds are specifield."""

        model = CustomUser
        fields = ["email", "first_name", "last_name", "patronymic",
                  "phone_number", "bio", "avatar"]

    def clean_password2(self):
        """Check that the two password entries match."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """Save the provided password in hashed format."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """A form for updating users.

    Includes all the fields on the user, but replaces the password field with
    admin"s disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        """Meta class for specifing CustomUser model and its fields."""

        model = CustomUser
        fields = ("email", "password", "is_active")

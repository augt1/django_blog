from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.core.image_utils import delete_image_and_thumbnails

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
    )


class UserRegistrationForm(forms.ModelForm):
    ROLE_CHOICES = [
        ("author", "Author"),
        ("editor", "Editor"),
    ]

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your Password."}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm your password"}),
    )

    role = forms.ChoiceField(
        label="Register as",
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={"placeholder": "Select your role"}),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError("Passwords are not the same")
        return password2

    def save(self, commit=True):
        new_user = super().save(commit=False)
        new_user.is_staff = False
        new_user.set_password(self.cleaned_data.get("password"))

        if commit:
            new_user.save()

        role = self.cleaned_data.get("role").title() + "s"
        group, _ = Group.objects.get_or_create(name=role)
        new_user.groups.add(group)


class UserAdminForm(forms.ModelForm):
    def save(self, commit=True, *args, **kwargs):
        instance = super().save(commit=False)

        if instance.pk and "image" in self.changed_data:
            delete_image_and_thumbnails(instance)

        if commit:
            instance.save()
            self.save_m2m()

        return instance

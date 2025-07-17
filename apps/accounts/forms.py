from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

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

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email already exists.")
        return email

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError("Passwords are not the same")
        return password2

    def save(self, commit=True):
        new_user = super().save(commit=False)
        new_user.username = self.cleaned_data.get("email").split("@")[0]
        new_user.is_staff = True
        new_user.set_password(self.cleaned_data.get("password"))

        if commit:
            new_user.save()

        role = self.cleaned_data.get("role").title() + "s"
        group, _ = Group.objects.get_or_create(name=role)
        new_user.groups.add(group)


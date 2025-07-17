from django.contrib.auth import views
from django.shortcuts import redirect, render

from apps.accounts.forms import UserRegistrationForm


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect("accounts:login")
    else:
           
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})

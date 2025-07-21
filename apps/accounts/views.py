from django.contrib.auth import views
from django.shortcuts import redirect, render

from apps.accounts.forms import UserRegistrationForm
from apps.core.utils import verify_turnistile_token


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        verified_token = verify_turnistile_token(request)

        if not verified_token:
            return render(
                request,
                "accounts/register.html",
                {"form": form, "error": "Please complete the Turnstile challenge."},
            )

        if form.is_valid():
            form.save(commit=True)
            return redirect("accounts:login")
        else:
            if "comments" in form.errors:
                print("Honeypot field triggered, bot detected during registration.")

                return render(request, "accounts/register.html", {"form": form})
    else:

        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})

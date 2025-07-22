from django.contrib.auth import views
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from apps.accounts.forms import UserRegistrationForm
from apps.core.utils import verify_turnistile_token
from apps.core.decorators import user_owns_resource


User = get_user_model()


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


@login_required 
@user_owns_resource(param_name='user_id')
def user_profile_view(request, user_id):
    user_qs = User.objects.prefetch_related('posts', 'editable_posts')
    user = get_object_or_404(user_qs, id=user_id)

    return render(request, "accounts/user_profile.html", {"user": user})

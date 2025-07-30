from django.contrib.auth import get_user_model, views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.forms import UserRegistrationForm
from apps.core.decorators import user_owns_resource
from apps.core.turnstile_client import verify_turnstile_token

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        verified_token = verify_turnstile_token(request)

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

        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
@user_owns_resource(param_name="user_id")
def user_profile_view(request, user_id):
    user_qs = User.objects.prefetch_related("posts", "editable_posts")
    user = get_object_or_404(user_qs, uuid=user_id)

    return render(request, "accounts/user_profile.html", {"user": user})

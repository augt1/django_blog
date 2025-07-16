from django.contrib.auth import views
from django.shortcuts import redirect, render

from apps.accounts.forms import UserRegistrationForm


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data["password"])

            new_user.save()

            return redirect("blog:posts_list")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})

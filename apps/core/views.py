from django.shortcuts import redirect
from django.urls import reverse


def set_timezone(request):

    print(request.POST)

    request.session["user_timezone"] = request.POST["timezone"]

    return redirect(reverse("blog:posts_list"))
    
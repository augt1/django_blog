import datetime
import zoneinfo
from datetime import datetime, time

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.blog.forms import CommentForm, FilterForm, PostForm
from apps.core.akismet_client import AkismetClient, AkismetClientError
from apps.core.turnstile_client import verify_turnstile_token

from .models import Post

User = get_user_model()


def posts_list(request):
    published_posts = (
        Post.published.select_related("author")
        .prefetch_related("tags", "editors")
        .all()
    )

    search_query = request.GET.get("search", "")
    if search_query:
        published_posts = published_posts.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )

    filter_form = FilterForm(request.GET)

    if filter_form.is_valid():

        authors_query = filter_form.cleaned_data.get("authors")
        tags_query = filter_form.cleaned_data.get("tags")
        published_from_query = filter_form.cleaned_data.get("published_from", "")
        published_to_query = filter_form.cleaned_data.get("published_to", "")

        if published_from_query:
            published_posts = published_posts.filter(
                published_at__gte=published_from_query
            )
        if published_to_query:
            published_posts = published_posts.filter(
                published_at__lte=published_to_query
            )
        if authors_query:
            published_posts = published_posts.filter(author_id__in=authors_query)
        if tags_query:
            published_posts = published_posts.filter(
                tags__slug__in=tags_query
            ).distinct()

    paginator = Paginator(published_posts, 5)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    context = {
        "posts": posts,
        "filter_form": filter_form,
    }

    return render(request, "blog/posts_list.html", context)


def post_detail(request, year, month, day, slug):
    qs = Post.published.select_related("author").prefetch_related("tags", "editors")

    dt = datetime(year, month, day)

    start_dt = timezone.make_aware(
        datetime.combine(dt, time.min), timezone=zoneinfo.ZoneInfo("UTC")
    )
    end_dt = timezone.make_aware(
        datetime.combine(dt, time.max), timezone=zoneinfo.ZoneInfo("UTC")
    )

    post = get_object_or_404(
        qs,
        status=Post.Status.PUBLISHED,
        published_at__range=(start_dt, end_dt),
        slug=slug,
    )

    comments = post.comments.filter(active=True)

    comment_form = CommentForm()

    return render(
        request,
        "blog/post_detail.html",
        {"post": post, "comments": comments, "comment_form": comment_form},
    )


@login_required
def edit_post_view(request, slug):
    post = get_object_or_404(
        Post.published.select_related("author").prefetch_related("tags", "editors"),
        slug=slug,
    )

    if not (
        request.user == post.author or post.editors.filter(pk=request.user.pk).exists()
    ):
        login_url = reverse("accounts:login")
        current_url = request.get_full_path()
        redirect_url = f"{login_url}?next={current_url}"
        return redirect(redirect_url)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post, user=request.user)

        if form.is_valid():
            post = form.save()

            return redirect(post.get_absolute_url())

    else:
        form = PostForm(instance=post, user=request.user)

    return render(request, "blog/edit_post_form.html", {"form": form, "post": post})


@require_POST
def create_comment_view(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    verified_turnstile_token = verify_turnstile_token(request)
    if not verified_turnstile_token:
        form.add_error(
            None, "Verification failed. Please try submitting the comment again."
        )
        comments = post.comments.filter(active=True)
        return render(
            request,
            "blog/post_detail.html",
            {"comment_form": form, "post": post, "comments": comments},
        )

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user_ip = request.META.get("REMOTE_ADDR")

        akismet_client = AkismetClient()

        try:
            #  no need to run verify_key on every call, can run when inserting key in the app, on demand or periodically
            # is_valid_key = akismet_client.verify_key()

            # if not is_valid_key:
            #     form.add_error(None, "A server error occured.")
            #     print("Invalid Akismet API key.")
            # else:
            akismet_data = {
                "user_ip": comment.user_ip,
                "comment_content": form.cleaned_data.get("content"),
                "comment_author": form.cleaned_data.get("name"),
                "comment_type": "comment",
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "referrer": request.META.get("HTTP_REFERER", ""),
            }

            result = akismet_client.comment_check(**akismet_data)
            status = result["status"]
            message = result["message"]

            if status == "discard":
                messages.error(request, message)
                return redirect(post.get_absolute_url())

            if status == "spam":
                comment.is_spam = True
                comment.active = False
                messages.error(request, message)
            else:  # ham
                comment.is_spam = False
                comment.active = True
                messages.success(request, message)

            comment.save()
            return redirect(post.get_absolute_url())

        except AkismetClientError as e:
            message = f"Akismet error: {str(e)}"
            messages.error(request, message)

        except Exception as e:
            message = f"An unexpected error occurred: {str(e)}"
            messages.error(request, message)

    comments = post.comments.filter(active=True)
    return render(
        request,
        "blog/post_detail.html",
        {"comment_form": form, "post": post, "comments": comments},
    )

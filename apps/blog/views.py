from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.blog.forms import CommentForm, FilterForm, PostForm

from .models import Post

User = get_user_model()


def posts_list(request):
    published_posts = (
        Post.published.select_related("author")
        .prefetch_related("tags", "editors")
        .all()
    )

    # handle filters
    search_query = request.GET.get("search", "")
    authors_query = request.GET.getlist("authors", [])
    tags_query = request.GET.getlist("tags", [])
    published_from_query = request.GET.get("published_from", "")
    published_to_query = request.GET.get("published_to", "")

    if published_from_query:
        published_posts = published_posts.filter(published_at__gte=published_from_query)
    if published_to_query:
        published_posts = published_posts.filter(published_at__lte=published_to_query)
    if search_query:
        published_posts = published_posts.filter(
            Q(title__icontains=search_query) | Q(content__icontains=search_query)
        )
    if authors_query:
        published_posts = published_posts.filter(author_id__in=authors_query)
    if tags_query:
        published_posts = published_posts.filter(tags__in=tags_query).distinct()

    paginator = Paginator(published_posts, 5)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    context = {
        "posts": posts,
    }

    if request.headers.get("HX-Request"):
        return render(request, "blog/partials/post_list_partial.html", context)

    filter_form = FilterForm()
    context["filter_form"] = filter_form

    return render(request, "blog/posts_list.html", context)


def post_detail(request, year, month, day, slug):
    qs = Post.published.select_related("author").prefetch_related("tags", "editors")
    post = get_object_or_404(
        qs,
        status=Post.Status.PUBLISHED,
        published_at__year=year,
        published_at__month=month,
        published_at__day=day,
        slug=slug,
    )

    comments = post.comments.filter(active=True)

    return render(
        request, "blog/post_detail.html", {"post": post, "comments": comments}
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


def create_comment_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

            return render(request, "blog/partials/comment.html", {"comment": comment})
        else:
            if "email" in form.errors:
                print(f"Honeypot field triggered, bot detected on post {post_id}.")

                return HttpResponse("")
    else:
        form = CommentForm()

    return render(
        request, "blog/partials/create_comment_form.html", {"form": form, "post": post}
    )

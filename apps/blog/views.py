from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from apps.blog.forms import FilterForm

from .models import Post

User = get_user_model()


def posts_list(request):
    published_posts = Post.published.prefetch_related("tags").all()

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

    paginator = Paginator(published_posts, 2)
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


# def post_list_partial(request):
#     published_posts = Post.published.prefetch_related("tags").all()

#     # handle filters
#     search_query = request.GET.get("search", "")

#     if search_query:
#         published_posts = published_posts.filter(Q(title__icontains=search_query)|
#                                                 Q(content__icontains=search_query))

#     paginator = Paginator(published_posts, 2)
#     page_number = request.GET.get("page")
#     posts = paginator.get_page(page_number)

#     return render(request, "blog/partials/post_list_partial.html", {"posts": posts})


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        published_at__year=year,
        published_at__month=month,
        published_at__day=day,
        slug=slug,
    )

    return render(request, "blog/post_detail.html", {"post": post})

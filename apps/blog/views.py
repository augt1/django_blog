from django.shortcuts import get_object_or_404, render

from .models import Post


def posts_list(request):
    posts = Post.published.all()

    return render(request, "blog/posts_list.html", {"posts": posts})


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        publish_date__year=year,
        publish_date__month=month,
        publish_date__day=day,
        slug=slug,
    )

    return render(request, "blog/post_detail.html", {"post": post})

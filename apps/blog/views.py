from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.blog.forms import CommentForm, FilterForm, PostForm
from apps.core.akismet_client import AkismetClient, AkismetClientError
from apps.core.utils import verify_turnistile_token

from .models import Post, Comment

User = get_user_model()


def posts_list(request):
    published_posts = (
        Post.published.select_related("author")
        .prefetch_related("tags", "editors")
        .all()
    )

    print(request.GET)
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
        published_posts = published_posts.filter(tags__slug__in=tags_query).distinct()

    paginator = Paginator(published_posts, 5)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    filter_form = FilterForm(request.GET)

    context = {
        "posts": posts,
        "filter_form": filter_form,
    }

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

    comment_form = CommentForm()

    return render(
        request, "blog/post_detail.html", {
            "post": post, 
            "comments": comments,
            "comment_form": comment_form}
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

    verified_token = verify_turnistile_token(request)

    if not verified_token:
        form.add_error(None, "Please complete the Turnstile challenge.")


    if form.is_valid():
        print("FORM IS VALID")
        comment = form.save(commit=False)
        comment.post = post
        comment.user_ip = request.META.get("REMOTE_ADDR")

        akismet_client = AkismetClient()
        
        try:

            is_valid_key = akismet_client.verify_key()

            if not is_valid_key:
                form.add_error(None, "A server error occured.")
                print("Invalid Akismet API key.")
            else:

                result = akismet_client.comment_check(
                    user_ip=comment.user_ip,
                    comment_content=form.cleaned_data.get("content"),
                    comment_author=form.cleaned_data.get("name"),
                    comment_type="comment",
                )
                message = result["message"]

                if result["status"] == "spam":
                    print("Comment is SPAM")
                    comment.is_spam = True
                    comment.active = False

                # if result["status"] == "discard":

                comment.save()

                form = CommentForm()

        except AkismetClientError as e:
            message = f"Akismet error: {str(e)}"


        except Exception as e:
            message = f"An unexpected error occurred: {str(e)}"

    else:
        if "email" in form.errors:
            print(f"Honeypot field triggered, bot detected on post {post_id}.")

            return HttpResponse("")
    
    comments = post.comments.filter(active=True)
    
    return render(
        request, "blog/post_detail.html", {
            "comment_form": form, 
            "post": post,
            "comments": comments}
    )

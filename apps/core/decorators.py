from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from apps.blog.models import Post

def user_owns_resource(param_name='user_id'):
    """
    Decorator to check if request.user.id matches the value of a parameter from the URL (e.g., 'user_id').
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_id = kwargs.get(param_name)

            if str(request.user.id) != str(user_id) and not request.user.is_superuser:
                return HttpResponseForbidden("You are not authorized to access this resource.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def user_is_author_or_editor(post_id_kwarg='post_id'):
    """
    Decorator to check if request.user is the author or an editor of the post.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            post_id = kwargs.get(post_id_kwarg)
            post_qs = Post.objects.prefetch_related('editors').select_related('author')
            post = get_object_or_404(post_qs, id=post_id)

            user = request.user
            if post.author != user and user not in post.editors.filter(id=user.id) and not user.is_superuser:
                return HttpResponseForbidden("You are not authorized to access this post.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

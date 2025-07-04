from django.urls import path

from apps.blog import views

app_name = "blog"

urlpatterns = [
    path("", views.posts_list, name="posts_list"),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:slug>/",
        views.post_detail,
        name="post_detail",
    ),
    path("partials/post_list/", views.post_list_partial, name="post_list_partial"),
    # path("tags/<slug:slug>/", views.tag_detail, name="tag_detail"),
]

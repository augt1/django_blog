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
    path("post/<slug:slug>", views.edit_post_view, name="edit_post"),
    # path("tags/<slug:slug>/", views.tag_detail, name="tag_detail"),
]

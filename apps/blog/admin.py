from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.html import format_html
from django.utils.text import Truncator
from easy_thumbnails.files import get_thumbnailer

from apps.blog.forms import PostAdminForm
from apps.blog.models import Comment, Post, Tag
from apps.core.akismet_client import AkismetClient
from apps.core.utils import delete_image_and_thumbnails


User = get_user_model()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = [
        "name",
    ]
    list_per_page = 20

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff


@admin.action(description="Mark selected comments as spam")
def mark_comments_as_spam(modeladmin, request, queryset):
    akismet_client = AkismetClient()

    for comment in queryset:
        akismet_client.submit_spam(
            user_ip=comment.user_ip,
            comment_content=comment.content,
            comment_author=comment.name,
            comment_type="comment",
        ) 
        
    queryset.update(is_spam=True, active=False)

@admin.action(description="Mark selected comments as not spam(ham)")
def mark_comments_as_ham(modeladmin, request, queryset):
    akismet_client = AkismetClient()

    for comment in queryset:
        akismet_client.submit_ham(
            user_ip=comment.user_ip,
            comment_content=comment.content,
            comment_author=comment.name,
            comment_type="comment",
        ) 
        
    queryset.update(is_spam=True, active=False)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["name", "post", "created_at", "active", "is_spam"]
    search_fields = ["post__title", "name", "content"]
    list_filter = ["active", "is_spam", "created_at"]
    list_per_page = 20
    actions = [
        mark_comments_as_spam,
        mark_comments_as_ham,
    ]


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("name", "truncated_content", "created_at", "active")
    readonly_fields = ("created_at", "truncated_content")

    @admin.display(description="Content (truncated)")
    def truncated_content(self, obj):
        return Truncator(obj.content).words(20, truncate="...")
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.action(description="Publish selected posts")
def post_update_status_published_action(modeladmin, request, queryset):
    queryset.update(status=Post.Status.PUBLISHED)
    queryset.update(published_at=timezone.now())


@admin.action(description="Unpublish selected posts")
def post_update_status_draft_action(modeladmin, request, queryset):
    queryset.update(status=Post.Status.DRAFT)
    queryset.update(published_at=None)


@admin.action(description="Archive selected posts")
def post_update_status_archive_action(modeladmin, request, queryset):
    queryset.update(status=Post.Status.ARCHIVED)
    queryset.update(published_at=None)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = [
        "title",
        "author",
        "status",
        "published_at",
        "created_at",
        "image_thumbnail",
        "tags_list",
        "total_comments",
    ]
    search_fields = [
        "title",
        "content",
        "author__first_name",
        "author__last_name",
        "author__email",
    ]

    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ["status", "-published_at", "-created_at"]
    autocomplete_fields = ["author", "tags", "editors"]
    actions = [
        post_update_status_published_action,
        post_update_status_draft_action,
        post_update_status_archive_action,
    ]
    inlines = [CommentInline]
    list_per_page = 20

    class Media:
        js = [
            "https://cdn.tiny.cloud/1/1acr1awsu4kzcz8efm1e45ma95nlrpqwbspquyy9e8tev24a/tinymce/7/tinymce.min.js",
            "js/tinymce_init.js",
        ]

    def delete_model(self, request, obj):
        if obj.image:
            delete_image_and_thumbnails(obj, delete=True)
        super().delete_model(request, obj)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("author").prefetch_related("tags", "editors")
        qs = qs.annotate(
            total_comments=Count("comments"),
        )

        if request.user.is_superuser:
            return qs
        return qs.filter(Q(author=request.user) | Q(editors=request.user))

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True

        return request.user == obj.author or request.user in obj.editors.all()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return request.user == obj.author or request.user in obj.editors.all()

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return False
        return request.user == obj.author

    def has_module_permission(self, request):
        return request.user

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            "image_preview",
        ]

        if obj:  # editing form
            readonly_fields += ["created_at", "updated_at"]

            if request.user in obj.editors.all() and not request.user.is_superuser:
                editable_fields = ["title", "content", "image", "tags", "slug"]
                all_fields = self.get_fields(request)
                readonly_fields = [f for f in all_fields if f not in editable_fields]
                readonly_fields += [
                    "image_preview",
                    "created_at",
                    "updated_at",
                ]  # ensure these are always readonly

        if not request.user.is_superuser:
            readonly_fields.append("author")

        return list(set(readonly_fields))

    def get_list_filter(self, request):
        list_filter = [
            "status",
            "published_at",
        ]

        if request.user.is_superuser:
            list_filter.append("author__email")
        return list_filter

    def get_fieldsets(self, request, obj=None):
        base_fields = [
            "title",
            "content",
            "tags",
            "editors",
            "slug",
            "status",
            "image",
            "image_preview",
        ]

        if request.user.is_superuser:
            base_fields.insert(1, "author")

        timestamp_fields = ["published_at"]

        if obj:  # editing form
            timestamp_fields += ["created_at", "updated_at"]

        fieldsets = (
            (None, {"fields": base_fields}),
            ("Timestamps", {"fields": timestamp_fields, "classes": ["collapse"]}),
        )

        return fieldsets

    def total_comments(self, obj):
        return obj.comments.count()

    @admin.display(description="Image")
    def image_thumbnail(self, obj):
        if obj.image:
            image_url = get_thumbnailer(obj.image)["post_thumbnail"].url
            return format_html('<img src="{}"/>', image_url)

        return "No image"

    @admin.display(description="Image Preview")
    def image_preview(self, obj):
        if obj.image:
            image_url = get_thumbnailer(obj.image)["post_preview"].url

            return format_html('<img src="{}"/>', image_url)
        return "No image uploaded"

    @admin.display(description="Tags")
    def tags_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    def total_comments(self, obj):
        return obj.total_comments


class PostInline(admin.TabularInline):
    model = Post
    extra = 1
    fields = ("title", "truncated_content", "status", "published_at")
    readonly_fields = ("published_at", "truncated_content")

    @admin.display(description="Content (truncated)")
    def truncated_content(self, obj):
        return Truncator(obj.content).words(20, truncate="...")

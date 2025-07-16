from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from django.utils.text import Truncator
from easy_thumbnails.files import get_thumbnailer
from django.contrib.auth import get_user_model

from apps.blog.models import Post, Tag

User = get_user_model()


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
    list_display = [
        "title",
        "author",
        "status",
        "published_at",
        "created_at",
        "image_thumbnail",
        "tags_list",
    ]
    search_filter = [
        "title",
        "content",
        "author__username",
    ]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ["status", "-published_at", "-created_at"]
    # raw_id_fields = ["author"]
    autocomplete_fields = ["author", "tags", "editors"]
    actions = [
        post_update_status_published_action,
        post_update_status_draft_action,
        post_update_status_archive_action,
    ]

    class Media:
        js = [
            "https://cdn.tiny.cloud/1/1acr1awsu4kzcz8efm1e45ma95nlrpqwbspquyy9e8tev24a/tinymce/7/tinymce.min.js",
            "js/tinymce_init.js",
        ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

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

    def save_model(self, request, obj, form, change):
        if not change or not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            "image_preview",
        ]

        if obj:  # editing form
            readonly_fields += ["created_at", "updated_at"]
            

            if request.user in obj.editors.all():
                editable_fields = ["title", "content", "image", "tags", "slug"]
                all_fields = self.get_fields(request)
                readonly_fields = [
                    f
                    for f in all_fields
                    if f not in editable_fields
                ]
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
            list_filter.append("author__username")
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


class PostInline(admin.TabularInline):
    model = Post
    extra = 1
    fields = ("title", "truncated_content", "status", "published_at")
    readonly_fields = ("published_at", "truncated_content")

    @admin.display(description="Content (truncated)")
    def truncated_content(self, obj):
        return Truncator(obj.content).words(20, truncate="...")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = [
        "name",
    ]

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

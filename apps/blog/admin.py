from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.text import Truncator
from easy_thumbnails.files import get_thumbnailer

from apps.blog.models import Post


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
    ]
    list_filter = [
        "status",
        "published_at",
        "author__username",
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
    autocomplete_fields = ["author"]
    show_facets = admin.ShowFacets.ALWAYS
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


    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            "image_preview",
        ]
        if obj:  # editing form
            return readonly_fields + ["created_at", "updated_at"]
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        base_fields = [
            "title",
            "author",
            "content",
            "slug",
            "status",
            "image",
            "image_preview",
        ]

        timestamp_fields = ["published_at"]

        if obj:  # editing form
            timestamp_fields += ["created_at", "updated_at"]

        fieldsets = (
            (None, {"fields": base_fields}),
            ("Timestamps", {"fields": timestamp_fields, "classes": ["collapse"]}),
        )

        return fieldsets

    def image_thumbnail(self, obj):
        print("Thumbnail called for:", obj)
        if obj.image:
            image_url = get_thumbnailer(obj.image)["post_thumbnail"].url
            return format_html('<img src="{}"/>', image_url)

        return "No image"

    image_thumbnail.short_description = "Image"

    def image_preview(self, obj):
        if obj.image:
            image_url = get_thumbnailer(obj.image)["post_preview"].url

            return format_html('<img src="{}"/>', image_url)
        return "No image uploaded"

    image_preview.short_description = "Image Preview"


class PostInline(admin.TabularInline):
    model = Post
    extra = 1
    fields = ("title", "truncated_content", "status", "published_at")
    readonly_fields = ("published_at", "truncated_content")

    def truncated_content(self, obj):
        return Truncator(obj.content).words(20, truncate="...")

    truncated_content.short_description = "Content (truncated)"

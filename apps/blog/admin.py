from django.contrib import admin
from django.utils.text import Truncator

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "status",
        "published_at",
        "created_at",
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

    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "content", "status")}),
        (
            "Timestamps",
            {
                "fields": ("published_at",),
                "classes": ("collapse",),
            },
        ),
    )


class PostInline(admin.TabularInline):
    model = Post
    extra = 1
    fields = ("title", "truncated_content", "status", "published_at")
    readonly_fields = ("published_at", "truncated_content")

    def truncated_content(self, obj):
        return Truncator(obj.content).words(20, truncate="...")

    truncated_content.short_description = "Content (truncated)"

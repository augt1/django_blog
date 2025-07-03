from django.contrib import admin
from django.utils.text import Truncator

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "status",
        "publish_date",
        "created_at",
    ]
    list_filter = [
        "status",
        "publish_date",
        "author__username",
    ]
    search_filter = [
        "title",
        "content",
        "author__username",
    ]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "publish_date"
    ordering = ["status", "-publish_date", "-created_at"]
    # raw_id_fields = ["author"]
    autocomplete_fields = ["author"]
    show_facets = admin.ShowFacets.ALWAYS


class PostInline(admin.TabularInline):
    model = Post
    extra = 1
    fields = ("title", "truncated_content", "status", "publish_date")
    readonly_fields = ("publish_date", "truncated_content")

    def truncated_content(self, obj):
        return Truncator(obj.content).words(20, truncate="...")
    
    truncated_content.short_description = "Content (truncated)"

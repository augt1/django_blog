from django.contrib import admin

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




from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.blog.admin import PostInline


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "is_staff", 'is_active',"total_posts"]
    list_filter = ["is_staff", "is_active"]
    search_fields = ["username", "email"]
    ordering = ["username"]
    show_facets = admin.ShowFacets.ALWAYS

    def total_posts(self, obj):
        return obj.posts.count()

    inlines = [PostInline]

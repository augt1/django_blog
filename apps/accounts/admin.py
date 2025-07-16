from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from easy_thumbnails.files import get_thumbnailer

from apps.blog.admin import PostInline

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = [
        "username",
        "email",
        "is_staff",
        "is_active",
        "total_posts",
        "avatar",
    ]
    list_filter = ["is_staff", "is_active"]
    search_fields = ["username", "email"]
    ordering = ["username"]
    show_facets = admin.ShowFacets.ALWAYS

    def total_posts(self, obj):
        return obj.posts.count()

    inlines = [PostInline]

    readonly_fields = ["avatar_preview"]

    @admin.display(description="Avatar")
    def avatar(self, obj):
        if obj.image:
            image_url = get_thumbnailer(obj.image)["avatar"].url
            return format_html('<img src="{}"/>', image_url)

        return "No image"

    @admin.display(description="Avatar Preview")
    def avatar_preview(self, obj):
        if obj.image:
            image_url = get_thumbnailer(obj.image)["avatar"].url
            return format_html('<img src="{}" />', image_url)
        return "No avatar uploaded"

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff
    
from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.blog.admin import PostInline
from easy_thumbnails.files import get_thumbnailer
from django.utils.html import format_html


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    #TODO: make the username clickable and not the first column
    list_display = ["username", "email", "is_staff", 'is_active',"total_posts", "avatar", ]
    list_filter = ["is_staff", "is_active"]
    search_fields = ["username", "email"]
    ordering = ["username"]
    show_facets = admin.ShowFacets.ALWAYS

    def total_posts(self, obj):
        return obj.posts.count()

    inlines = [PostInline]

    readonly_fields = ["avatar_preview"]


    def avatar(self, obj):
        print("Thumbnail called for:", obj)
        if obj.image:
            image_url = get_thumbnailer(obj.image)['avatar'].url
            return format_html('<img src="{}"/>', image_url)
        
        return "No image"
    avatar.short_description = "Avatar"


    def avatar_preview(self, obj):
        if obj.image:
            image_url = get_thumbnailer(obj.image)['avatar'].url
            return format_html('<img src="{}" />', image_url)
        return "No avatar uploaded"
    avatar_preview.short_description = "Avatar Preview"

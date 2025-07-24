from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from easy_thumbnails.files import get_thumbnailer

from django.db.models import Count

from apps.accounts.forms import UserAdminForm
from apps.blog.admin import PostInline
from apps.core.utils import delete_image_and_thumbnails

User = get_user_model()




@admin.action(description="Mark selected users as staff")
def make_user_staff(modeladmin, request, queryset):        
    queryset.update(is_staff=True)

@admin.action(description="Remove staff status from selected users")
def remove_user_from_staff(modeladmin, request, queryset):
    queryset.update(is_staff=False)

@admin.action(description="Activate selected users")
def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description="Deactivate selected users")
def deactivate_users(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm

    list_display = [
        "username",
        "email",
        "is_staff",
        "is_active",
        "total_posts",
        "avatar",
        "groups_list",
    ]
    list_filter = ["is_staff", "is_active", "groups"]
    search_fields = ["username", "email"]
    ordering = ["username"]
    show_facets = admin.ShowFacets.ALLOW
    list_per_page = 20
    actions = [
        make_user_staff,
        remove_user_from_staff,
        activate_users,
        deactivate_users,
    ]

    def delete_model(self, request, obj):
        if obj.image:
            delete_image_and_thumbnails(obj, delete=True)
            
        super().delete_model(request, obj)

        

    @admin.display(description="Groups")
    def groups_list(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related("groups", )

        return qs.annotate(
            total_posts=Count("posts"),
        )

    def total_posts(self, obj):
        return obj.total_posts

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

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        
        is_author = request.user.groups.filter(name="Authors").exists()
        return request.user.is_staff and is_author


class GroupUserInline(admin.TabularInline):
    model = User.groups.through
    extra = 0
    verbose_name = "User"
    verbose_name_plural = "Users in this group"
    fields = [
        "user",
    ]
    readonly_fields = ["user"]
    can_delete = False


admin.site.unregister(Group)


@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    inlines = [GroupUserInline]

import datetime

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

from apps.blog.utils import post_image_upload_path
from apps.core.validators import validate_image_file, validate_image_size

from .managers import PublishedManager

User = get_user_model()


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=100)
    content = models.TextField()
    published_at = models.DateTimeField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=100)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    image = models.ImageField(
        upload_to=post_image_upload_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif"]),
            validate_image_size,
            validate_image_file,
        ],
    )
    tags = models.ManyToManyField("Tag", blank=True, related_name="posts")
    editors = models.ManyToManyField(User, blank=True, related_name="editable_posts")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]

    objects = models.Manager()
    published = PublishedManager()

    def get_absolute_url(self):
        dt = (
            self.published_at
            if self.status == self.Status.PUBLISHED
            else self.created_at
        )

        dt_utc = dt.astimezone(datetime.timezone.utc)

        return reverse(
            "blog:post_detail",
            kwargs={
                "year": dt_utc.year,
                "month": dt_utc.month,
                "day": dt_utc.day,
                "slug": self.slug,
            },
        )


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("blog:tag_detail", kwargs={"slug": self.slug})


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=50, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    is_spam = models.BooleanField(default=False)
    user_ip = models.GenericIPAddressField(blank=True, null=True, default="0.0.0.0")

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["created_at"]

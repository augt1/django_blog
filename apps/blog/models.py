from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

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
    # TODO: add image field, tags, categories, comments from users

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        # TODO: think ordering and add indexes
        ordering = ["-created_at"]

    objects = models.Manager()
    published = PublishedManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        if self.status == self.Status.DRAFT:
            self.published_at = None

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={
                "year": self.published_at.year,
                "month": self.published_at.month,
                "day": self.published_at.day,
                "slug": self.slug,
            },
        )

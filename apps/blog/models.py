from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.blog.utils import post_image_upload_path
from apps.core.utils import delete_image_and_thumbanails
from apps.core.validators import validate_image_size

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
        ],
    )
    tags = models.ManyToManyField("Tag", blank=True, related_name="posts")
    editors = models.ManyToManyField(User, blank=True, related_name="editable_posts")

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
        # Find is old image exists and is not the same as the new one
        if self.pk:
            old_image = Post.objects.get(pk=self.pk).image
            if old_image and old_image != self.image:
                delete_image_and_thumbanails(old_image)

        if not self.slug:
            self.slug = slugify(self.title)

        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        if self.status == self.Status.DRAFT:
            self.published_at = None

        super().save(*args, **kwargs)

    def delete(self):
        if self.image:
            delete_image_and_thumbanails(self.image)
        super().delete()

    def get_absolute_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={
                "year": (
                    self.published_at.year
                    if self.status == self.Status.PUBLISHED
                    else self.created_at.year
                ),
                "month": (
                    self.published_at.month
                    if self.status == self.Status.PUBLISHED
                    else self.created_at.month
                ),
                "day": (
                    self.published_at.day
                    if self.status == self.Status.PUBLISHED
                    else self.created_at.day
                ),
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

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save()

    def get_absolute_url(self):
        return reverse("blog:tag_detail", kwargs={"slug": self.slug})

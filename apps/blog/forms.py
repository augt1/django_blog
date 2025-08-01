from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.group_assignments import (
    assign_user_groups,
    handle_old_author,
    handle_old_editors,
)
from apps.blog.models import Comment, Post, Tag
from apps.core.image_utils import delete_image_and_thumbnails

User = get_user_model()


class FilterForm(forms.Form):
    authors = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select2"}),
        label="Authors",
    )

    tags = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select2"}),
        label="Tags",
    )

    published_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Published From",
    )
    published_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Published To",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].choices = [
            (tag.slug, tag.name) for tag in Tag.objects.all()
        ]
        self.fields["authors"].queryset = User.objects.filter(is_staff=True)

    def clean_published_from(self):
        from_date = self.cleaned_data.get("published_from")
        if from_date:
            # convert to datetime and start fo day
            from_date_datetime = timezone.datetime.combine(
                from_date, timezone.datetime.min.time()
            )

            # make aware, default timezone to seting TIME_ZONE
            local_time = timezone.make_aware(from_date_datetime)

            return local_time
        else:
            return None

    def clean_published_to(self):
        to_date = self.cleaned_data.get("published_to")
        if to_date:
            # convert to datetime and end of day
            to_date_datetime = timezone.datetime.combine(
                to_date, timezone.datetime.max.time()
            )
            # make aware, default timezone to seting TIME_ZONE
            aware_time = timezone.make_aware(to_date_datetime)
            local_time = timezone.localtime(aware_time)

            return local_time
        else:
            return None

    def clean(self):
        from_date = self.cleaned_data.get("published_from")
        to_date = self.cleaned_data.get("published_to")

        if to_date and from_date:

            if to_date < from_date:
                raise forms.ValidationError("Publish From cannot be after Publish To")


class BasePostForm(forms.ModelForm):
    def clean_published_at(self):
        published_at = self.cleaned_data.get("published_at")
        status = self.cleaned_data.get("status")

        if status == Post.Status.PUBLISHED and not published_at:
            return timezone.now()
        if status == Post.Status.DRAFT:
            return None

        return published_at

    def save(self, commit=True, *args, **kwargs):
        instance = super().save(commit=False)

        if instance.pk and "image" in self.changed_data:
            delete_image_and_thumbnails(instance)

        if instance.pk and "author" in self.changed_data:
            handle_old_author(instance)

        if instance.pk and "editors" in self.changed_data:
            new_editors = self.cleaned_data.get("editors")
            handle_old_editors(instance, new_editors)

        if commit:
            print("inside commit true")
            instance.save()
            self.save_m2m()
            if "author" in self.changed_data or "editors" in self.changed_data:
                assign_user_groups(
                    self.cleaned_data.get("author"), self.cleaned_data.get("editors")
                )

        return instance


class PostForm(BasePostForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "status",
            "slug",
            "author",
            "editors",
            "image",
            "published_at",
            "tags",
        ]
        widgets = {
            "title": forms.TextInput(),
            "content": forms.Textarea(),
            "author": forms.Select(attrs={"class": "select2"}),
            "slug": forms.TextInput(),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "status": forms.Select(),
            "tags": forms.SelectMultiple(attrs={"class": "select2"}),
            "editors": forms.SelectMultiple(attrs={"class": "select2"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        if self.instance and self.user:
            is_author = self.user == self.instance.author
            is_editor = self.user in self.instance.editors.all()

            if is_editor and not is_author:
                readonly_fields = ["author", "editors", "published_at"]
                for field in readonly_fields:
                    if field in self.fields:
                        self.fields[field].disabled = True

        self.fields["editors"].queryset = User.objects.filter(is_staff=True).exclude(
            id=self.instance.author_id
        )


class PostAdminForm(BasePostForm):
    pass


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["name", "content"]

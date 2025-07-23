from django import forms
from django.contrib.auth import get_user_model

from apps.blog.models import Comment, Post, Tag

User = get_user_model()


class FilterForm(forms.Form):
    authors = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select2"}),
        label="Authors",
    )
    # tags = forms.ModelMultipleChoiceField(
    #     queryset=Tag.objects.all(),
    #     required=False,
    #     widget=forms.SelectMultiple(attrs={"class": "select2"}),
    #     label="Tags",
    # )
    tags = forms.MultipleChoiceField(
        choices=[(tag.slug, tag.name) for tag in Tag.objects.all()],
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


class PostForm(forms.ModelForm):
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
            "published_at": forms.DateTimeInput(),
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

        self.fields['editors'].queryset = User.objects.filter(is_staff=True).exclude(id=self.instance.author_id)


class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ["name", "content"]
from django import forms
from django.contrib.auth import get_user_model

from apps.blog.models import Post, Tag

User = get_user_model()


class FilterForm(forms.Form):
    # status = forms.ChoiceField(
    #     choices=[(""), ("All")] + Post.Status.choices,
    #     required=False,
    #     widget=forms.Select(attrs={"class": "select2"}),
    #     label="Status",
    # )
    authors = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select2"}),
        label="Authors",
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
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

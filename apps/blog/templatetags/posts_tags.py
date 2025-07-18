from django import template

register = template.Library()

@register.filter
def can_edit_post(post, user):
    return post.author == user or post.editors.filter(pk=user.pk).exists()

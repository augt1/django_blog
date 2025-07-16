from django import template

register = template.Library()

@register.filter
def can_edit_post(post, user):
    return post.author == user or user in post.editors.all()

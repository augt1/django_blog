from django.contrib.auth.models import Group


def assign_user_groups(author, editors):
    if author:
        authors_group, _ = Group.objects.get_or_create(name="Authors")
        print(f"Added {author} to 'Authors' group")
        author.groups.add(authors_group)
    
    if editors:
        editors_group, _ = Group.objects.get_or_create(name="Editors")
        for editor in editors:
            print(f"Added {editor} to 'Editors' group")
            editor.groups.add(editors_group)


def handle_old_author(instance):
    old_author = instance.__class__.objects.get(pk=instance.pk).author
    new_author = instance.author

    if old_author != new_author:
        is_author_to_other_posts = (
            instance.__class__.objects.filter(author=old_author)
            .exclude(pk=instance.pk)
            .exists()
        )

        if not is_author_to_other_posts:
            authors_group, _ = Group.objects.get_or_create(name="Authors")
            old_author.groups.remove(authors_group)


def handle_old_editors(instance, new_editors):
    old_editors = instance.__class__.objects.get(pk=instance.pk).editors.all()

    removed_editors = list(set(old_editors) - set(new_editors))

    if removed_editors:

        for editor in removed_editors:
            is_editor_to_other_posts = (
                instance.__class__.objects.filter(editors=editor)
                .exclude(pk=instance.pk)
                .exists()
            )

            if not is_editor_to_other_posts:
                editors_group, _ = Group.objects.get_or_create(name="Editors")
                editor.groups.remove(editors_group)
            
from django.core.management.base import BaseCommand
from apps.blog.factories import PostPublishedFactory


class Command(BaseCommand):
    help = 'Populate the database with posts'

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=20)

    def handle(self, *args, **kwargs):
        number = kwargs['number']

        for _ in range(number):
            post = PostPublishedFactory()
            self.stdout.write(
                self.style.SUCCESS(f'Post "{post.title}" created with author "{post.author.username}"')
            )



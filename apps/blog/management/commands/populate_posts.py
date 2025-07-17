from django.core.management.base import BaseCommand
from apps.blog.factories import PostPublishedFactory

class Command(BaseCommand):
    help = "Populate the database with posts"

    def add_arguments(self, parser):
        parser.add_argument(
            '--number', '-n', type=int, default=10,
            help='Number of posts to create (default: 10)'
        )

    def handle(self, *args, **kwargs):
        number = kwargs['number']
        self.stdout.write(f"Creating {number} posts...")

        posts = PostPublishedFactory.create_batch(number)

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(posts)} posts."))

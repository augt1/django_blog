from django.core.management.base import BaseCommand
from apps.blog.factories import TagFactory

class Command(BaseCommand):
    help = "Populate the database with tags"

    def add_arguments(self, parser):
        parser.add_argument(
            '--number', '-n', type=int, default=10,
            help='Number of tags to create (default: 10)'
        )

    def handle(self, *args, **kwargs):
        number = kwargs['number']
        self.stdout.write(f"Creating {number} tags...")

        tags = TagFactory.create_batch(number)

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(tags)} tags."))

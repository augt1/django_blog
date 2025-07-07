from django.core.management.base import BaseCommand
from apps.accounts.factories import UserAuthorFactory


class Command(BaseCommand):
    help = 'Populate the database with users'

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=20)

    def handle(self, *args, **kwargs):
        number = kwargs['number']

        for _ in range(number):
            post = UserAuthorFactory()
            self.stdout.write(
                self.style.SUCCESS(f"Author '{post.username}' created with email '{post.email}'")
            )



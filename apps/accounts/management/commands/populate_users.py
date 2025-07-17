from django.core.management.base import BaseCommand

from apps.accounts.factories import UserAuthorFactory, UserEditorFactory


class Command(BaseCommand):
    help = "Populate the database with users"

    def add_arguments(self, parser):
        parser.add_argument(
            "-a", "--authors", type=int, default=20, help="Number of authors to create"
        )
        parser.add_argument(
            "-e", "--editors", type=int, default=0, help="Number of editors to create"
        )

    def handle(self, *args, **kwargs):
        authors_count = kwargs["authors"]
        editors_count = kwargs["editors"]

        for _ in range(authors_count):
            user = UserAuthorFactory()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Author '{user.username}' created with email '{user.email}'"
                )
            )

        for _ in range(editors_count):
            user = UserEditorFactory()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Editor '{user.username}' created with email '{user.email}'"
                )
            )

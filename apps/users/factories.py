import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.contrib.auth import get_user_model


User = get_user_model()
fake = Faker()


class UserAuthorFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.django.Password('testing123!@#')
    is_staff = True

    
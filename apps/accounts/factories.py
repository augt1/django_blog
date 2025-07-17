import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from factory.django import DjangoModelFactory
from faker import Faker

User = get_user_model()
fake = Faker()


class BaseUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.django.Password("testing123!@#")
    is_staff = True
    first_name = factory.LazyAttribute(lambda obj: obj.username.title())
    last_name = factory.LazyAttribute(lambda obj: obj.username.title())


class UserAuthorFactory(BaseUserFactory):
    username = factory.Sequence(lambda n: f"author{n}")

    @factory.post_generation
    def add_to_group(self, create, extracted, **kwargs):
        if not create:
            return
        group, _ = Group.objects.get_or_create(name="Authors")
        self.groups.add(group)


class UserEditorFactory(BaseUserFactory):
    username = factory.Sequence(lambda n: f"editor{n}")
    
    @factory.post_generation
    def add_to_group(self, create, extracted, **kwargs):
        if not create:
            return
        group, _ = Group.objects.get_or_create(name="Editors")
        self.groups.add(group)

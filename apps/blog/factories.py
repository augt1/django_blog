import random
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from apps.blog.models import Post, Tag
from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()
fake = Faker()


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.LazyFunction(lambda: fake.unique.word())



class PostPublishedFactory(DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker('sentence', nb_words=6)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))
    content = factory.Faker('paragraph', nb_sentences=15)
    author = factory.Iterator(User.objects.filter(is_staff=True))    
    published_at = factory.Faker('date_time_this_year', before_now=True)
    status = Post.Status.PUBLISHED

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            all_tags = list(Tag.objects.all())
            selected = random.sample(all_tags, min(len(all_tags), random.randint(1, 3)))
            self.tags.add(*selected)
    
    @factory.post_generation
    def editors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for editor in extracted:
                self.editors.add(editor)
        else:
            staff_users = list(User.objects.filter(is_staff=True).exclude(pk=self.author.pk))
            selected = random.sample(staff_users, min(len(staff_users), random.randint(1, 3)))
            self.editors.add(*selected)



    

    
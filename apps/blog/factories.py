import factory
from factory.django import DjangoModelFactory
from faker import Faker
from apps.blog.models import Post
from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()
fake = Faker()


class PostPublishedFactory(DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker('sentence', nb_words=6)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))
    content = factory.Faker('paragraph', nb_sentences=5)
    author = factory.Iterator(User.objects.filter(is_staff=True))    
    published_at = factory.Faker('date_time_this_year', before_now=True)
    status = Post.Status.PUBLISHED


    

    
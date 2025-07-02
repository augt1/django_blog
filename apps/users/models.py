from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    """
   
    pass

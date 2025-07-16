from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


class CustomEmailAuthenticationBackend:

    """
    Custom authentication backend that allows users to log in with their email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


from django.contrib.auth.backends import ModelBackend
from apps.common.models import User
from django.contrib.auth.hashers import check_password


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.using("default").get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.using("default").get(pk=user_id)
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, username):
        user = User.objects.using("default").get(username=username)
        return user.is_active

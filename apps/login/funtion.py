from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

def authenticate_custom(username=None, password=None):
    User = get_user_model()
    try:
        user = User.objects.using("default").get(username=username)
        if user.check_password(password):
            return user
        else:
            return None
    except User.DoesNotExist:
        return None
    
    ## default
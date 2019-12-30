from django.contrib.auth.models import User
from .models import MyUser

def get_user(request):
    myuser = None
    if request.user.is_authenticated:
        try:
            myuser = MyUser.objects.get(user=request.user)
        except Exception:
            myuser = None
    return {'myuser': myuser}

def get_subscribers(request):
    return {'subscribers': MyUser.objects.all().count()}
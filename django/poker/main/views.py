from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import MyUser


def index(request):
    subscribers = MyUser.objects.all().count()
    context = {'subscribers': subscribers}
    return render(request, 'main/index.html', context)

@transaction.atomic
def signup(request):
    context = dict()
    if request.POST:
        try:
            user = User()        
            user.first_name = request.POST['name']
            if not request.POST['username'].isalnum():
                raise Exception('Nickname must be alphanumeric!')
            user.username = request.POST['username']                   
            user.set_password(request.POST['password'])
            user.save()

            myuser = MyUser()
            myuser.user = user
            myuser.email = request.POST['email'] 
            myuser.country = request.POST['country']
            myuser.money = 30000
            myuser.save()

            authenticate(request, username=request.POST['username'], password=request.POST['password'])
            login(request, user)            
        except Exception as error:
            messages.add_message(request, messages.ERROR, 'Error: ' + str(error))
            context = {'show_signup': True}

    return render(request, 'main/index.html', context)

def signin(request):
    context = dict()
    if request.POST:
        try:
            myuser = MyUser.objects.get(email=request.POST['email'])
            user = authenticate(request, username=myuser.user.username, password=request.POST['password'])
            login(request, user)            
        except Exception as error:
            messages.add_message(request, messages.ERROR, 'Invalid email or password!')
            context = {'show_signin': True}

    return render(request, 'main/index.html', context)

def signout(request):
    logout(request)
    return render(request, 'main/index.html')

def contact(request):
    return render(request, 'main/index.html')


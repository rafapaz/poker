import datetime
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import MyUser


def index(request):
    return render(request, 'main/index.html')

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
            myuser.token = str(hash(datetime.datetime.now()))            
            myuser.save()

            if myuser.money == 0:
                diff = timezone.now() - myuser.time_zero
                print(diff)
                if diff.days >= 1:
                    myuser.money = 30000
                    myuser.save()

        except Exception as error:
            messages.add_message(request, messages.ERROR, 'Invalid email or password! ' + str(error))
            context = {'show_signin': True}

    return render(request, 'main/index.html', context)

def signout(request):
    logout(request)
    return render(request, 'main/index.html')

def contact(request):
    return render(request, 'main/index.html')

@login_required
def play(request):
    myuser = MyUser.objects.get(user=request.user)
    if myuser.money == 0:
        return render(request, 'main/index.html', {'show_cannotplay': True})

    return render(request, 'main/game.html', {'token': myuser.token})


def ack(request):    
    try:
        myuser = MyUser.objects.get(token=request.GET['token'])
        return HttpResponse('OK')
    except Exception:
        return HttpResponse('ERROR')


def update_money(request):
    if '127.0.0.1' in request.META['HTTP_HOST']:
        username = request.GET['name']
        money = request.GET['money']
        user = User.objects.get(username=username)
        myuser = MyUser.objects.get(user=user)
        myuser.money = money
        if money == 0:
            myuser.time_zero = datetime.datetime.now()
        myuser.save()
        return HttpResponse('OK')
    return HttpResponse('ERROR')
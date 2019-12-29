from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'main/index.html')

def signup(request):
    return render(request, 'main/index.html')

def signin(request):
    return render(request, 'main/index.html')

def contact(request):
    return render(request, 'main/index.html')

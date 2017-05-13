from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from ElectionServer.models import Election

# Create your views here.

#@login_required
def home(request):
    context = {'Elections': Election.objects.all()}
    return render(request,'home.html',context)

def login(request):
    return render(request,'login.html')
    
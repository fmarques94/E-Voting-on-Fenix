from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from ElectionServer.models import Election
from ElectionServer.forms import ElectionCreationForm
import uuid

# Create your views here.

#@login_required
def home(request):
    context = {'elections': Election.objects.all()}
    return render(request,'home.html',context)


def createElection(request):
    if request.method == 'POST':
        form = ElectionCreationForm(request.POST)
        if form.is_valid():
            newElection = Election()
            newElection.uuid = uuid.uuid4()
            newElection.name = form.cleaned_data['name']
            newElection.description = form.cleaned_data['description']
            newElection.start = form.cleaned_data['startTime']
            newElection.end = form.cleaned_data['endTime']
            newElection.timeOpenBooth = form.cleaned_data['timeOpenBooth']
            newElection.timeCloseBooth = form.cleaned_data['timeCloseBooth']
            newElection.admin = request.user
            newElection.save()
            return redirect(election)
    else:
        form = ElectionCreationForm()
        print(form)
        return render(request,'create.html',{'form':form})

def election(request):
    return render(request,'election.html')
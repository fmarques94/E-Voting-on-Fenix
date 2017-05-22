from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from ElectionServer.exceptions import TrusteeAlreadyPresentError

from ElectionServer.models import Election
from ElectionServer.forms import ElectionCreationForm
from ElectionServer.parser import *
import uuid
import json

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
            return redirect(manage,election_id = newElection.uuid)
    else:
        form = ElectionCreationForm()
        print(form)
        return render(request,'create.html',{'form':form})

def election(request,election_id):
    return render(request,'election.html')

def manage_list(request):
    context = {'elections': Election.objects.filter(admin=request.user)}
    return render(request,'manageList.html',context)

def manage(request,election_id):
    context = {'election': Election.objects.get(uuid=election_id)}
    return render(request,'manage.html',context)

def manageQuestions(request,election_id):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        parseQuestion(json.loads(data),election_id)
        payload = {'success': True}
        return HttpResponse(json.dumps(payload),content_type='application/json')
    else:
        election = Election.objects.get(uuid=election_id)
        context = {'election':Election.objects.get(uuid=election_id)}
        for question in election.question_set.all():
            print(question.question)
    return render(request, "manageQuestions.html",context)

def addVoters(request,election_id):
    context = {'election': Election.objects.get(uuid=election_id)}
    if request.POST and request.FILES:
        csvfile = request.FILES['voters']
        parseVoterFile(csvfile,election_id)
    return render(request,"addVoters.html",context)

def manageTrustees(request,election_id):
    context = {'election': Election.objects.get(uuid=election_id)}
    if request.method == 'POST':
        try:
            data = request.body.decode('utf-8')
            parseTrustees(json.loads(data),context['election'])
            payload = {'success': True}
            print("Success")
            return HttpResponse(json.dumps(payload),content_type='application/json')
        except TrusteeAlreadyPresentError:
            payload = {'err': 'Trustee is already present for this election'}
            response = HttpResponse(json.dumps(payload),content_type='application/json')
            response.status_code = 400
            return response
    return render(request,"manageTrustees.html",context)
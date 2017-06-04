from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from ElectionServer.exceptions import TrusteeAlreadyPresentError
from django.http import Http404

from ElectionServer.models import Election
from ElectionServer.forms import ElectionCreationForm
from ElectionServer.parser import *
from ElectionServer.Crypto.ParameterGenerator import generate_parameters
import uuid
import json

# Create your views here.

def home(request):
    context = {'elections': Election.objects.all()}
    return render(request,'home.html',context)

def login(request):
    return render(request,'login.html')

@login_required
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
            parameters = generate_parameters()
            newElection.p = parameters['p']
            newElection.q = parameters['q']
            newElection.g = parameters['g']
            newElection.save()
            return redirect(manage,election_id = newElection.uuid)
    else:
        form = ElectionCreationForm()
        print(form)
        return render(request,'create.html',{'form':form})

@login_required
def election(request,election_id):
    try:
        context = {'election': Election.objects.get(uuid=election_id)}
    except Election.DoesNotExist:
        raise Http404("Election does not exist")
    return render(request,'election.html')

@login_required
def manage_list(request):
    context = {'elections': Election.objects.filter(admin=request.user)}
    return render(request,'manageList.html',context)

@login_required
def manage(request,election_id):
    try:
        election = Election.objects.get(uuid=election_id)
    except Election.DoesNotExist:
        raise Http404("Election does not exist")
    if election.admin == request.user:
        context = {'election': election}
        return render(request,'manage.html',context)
    else:
        return HttpResponse('<h1>Error 401: Unauthorized</h1>', status=401)

@login_required
def manageQuestions(request,election_id):
    try:
        election = Election.objects.get(uuid=election_id)
    except Election.DoesNotExist:
        raise Http404("Election does not exist")
    if election.admin != request.user:
         return HttpResponse('<h1>Error 401: Unauthorized</h1>', status=401)
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        parseQuestion(json.loads(data),election_id)
        payload = {'success': True}
        return HttpResponse(json.dumps(payload),content_type='application/json')
    else:
        context = {'election':election}
        return render(request, "manageQuestions.html",context)

@login_required
def addVoters(request,election_id):
    try:
        election = Election.objects.get(uuid=election_id)
    except Election.DoesNotExist:
        raise Http404("Election does not exist")
    if election.admin != request.user:
         return HttpResponse('<h1>Error 401: Unauthorized</h1>', status=401)
    context = {'election': election}
    if request.POST and request.FILES:
        csvfile = request.FILES['voters']
        result = parseVoterFile(csvfile,context['election'])
        if result!=None :
            context['error'] = 'The voter with the id ' + result + ' is already added to the election'
    return render(request,"addVoters.html",context)

@login_required
def manageTrustees(request,election_id):
    try:
        election = Election.objects.get(uuid=election_id)
    except Election.DoesNotExist:
        raise Http404("Election does not exist")
    if election.admin != request.user:
         return HttpResponse('<h1>Error 401: Unauthorized</h1>', status=401)
    context = {'election': election}
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

@login_required
def trustee(request,election_id,trustee_id):
    try:
        election = Election.objects.get(uuid=election_id)
    except Election.DoesNotExist:
        raise Http404("Election does not exist")
    print(request.user.username)
    if request.user.username != trustee_id:
        return HttpResponse('<h1>Error 401: Unauthorized</h1>', status=401)
    trustee = election.trustee_set.all().filter(trusteeId=trustee_id).first()
    context = {'trustee': trustee,'election':election}
    if trustee:
        if request.method == 'POST':
            data = request.body.decode('utf-8')
            receiveKeyShare(json.loads(data),trustee)
            payload = {'success': True}
            print("Success")
            return HttpResponse(json.dumps(payload),content_type='application/json')
        else:
            print(trustee.name)
            return render(request,"trustee.html",context)
    else:
        return HttpResponse('<h1>Error 401: Unauthorized</h1>', status=401)


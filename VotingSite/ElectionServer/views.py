from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core import serializers
from django.http import HttpResponse, HttpResponseNotAllowed, Http404, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db import transaction

#Models
from ElectionServer.models import Election 
from ElectionServer.models import Trustee
from ElectionServer.models import Voter
from ElectionServer.models import Question
from ElectionServer.models import Answer

def home(request):
    context = {'elections': Election.objects.all()}
    return render(request,'home.html',context)

def login(request):
    return render(request,'login.html')

def getElections(request):
    if request.method == 'GET':
        data = serializers.serialize('json',list(Election.objects.all()))
        return HttpResponse(json.dumps(data),content_type='application/json')
    else:
        return HttpResponseNotAllowed(['GET'])

@login_required
def createElection(request):

    @csrf_exempt
    def postCreateElection(request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            parameters = generate_parameters()
            election = Election()
            election.name = data['name']
            election.description = data['description']
            election.startDate = data['startDate']
            election.endDate = data['endDate']
            election.openCastTime = data['openCastTime']
            election.closeCastTime = data['closeCastTime']
            election.admin = request.user
            election.cryptoParameters = {
                'p':parameters['p'],
                'q':parameters['q'],
                'g':parameters['g']
            }
            election.save()
            return HttpResponse(json.dumps({
                'success':True,
                'id':election.id
                }),content_type='application/json')
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')

    def getCreateElection(request):
        #TODO
    
    if request.method == 'POST':
        return postCreateElection(request)
    elif request.method == 'GET':
        return getCreateElection(request)
    else:
        return HttpResponseNotAllowed(['GET','POST'])

@login_required
def election(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        #TODO
    else:
        return HttpResponseNotAllowed(['GET'])

@login_required
@csrf_exempt
def addTrustees(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
            if request.user != election.admin:
                return HttpResponseForbidden("Access denied")
            data = json.loads(request.body.decode('utf-8'))
            with transaction.atomic():
                for trusteeData in data['trusteeList']:
                    trustee = Trustee()
                    trustee.election = election
                    trustee.id = trusteeData['id']
                    trustee.name = trusteeData['name']
                    trustee.email = trusteeData['email']
                    trustee.save()
            except Election.DoesNotExist:
                return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
            except Exception as exception:
                return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
@csrf_exempt
def removeTrustees(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        data = json.loads(request.body.decode('utf-8'))
        for trusteeData in data['trusteeList']:
            try:
                Trustee.objects.get(id=trusteeData['id'],election=election).delete()
            except Trustee.DoesNotExist:
                pass
            except Exception as exception:
                return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')  
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def addVoters(request,election_id):

    def addVotersFile(request,election):
        csvfile = request.FILES['voters']
        reader = csv.reader(csvfile.read().decode('utf-8-sig').split('\n'),delimiter=";")
        try:
            with transaction.atomic():
                for row in reader:
                    if(len(row)>0):
                        voter = Voter()
                        voter.election = election
                        voter.id = row[0]
                        voter.email = row[1]
                        voter.save()
        except IntegrityError:
            return HttpResponse(json.dumps({
                'error':'Voter with id ' + row[0] + 'is already in the election'
                }), content_type='application/json')
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')
        return HttpResponse(json.dumps({
                'success':True
                }), content_type='application/json')

    @csrf_exempt
    def addVotersJson(request,election):
        data = json.loads(request.body.decode('utf-8'))
        try:
            with transaction.atomic():
                for voterData in data['voterList']:
                    voter = Voter()
                    voter.election = election
                    voter.id = voterData['id']
                    voter.email = voterData['email']
                    voter.save()
        except IntegrityError:
            return HttpResponse(json.dumps({
                'error':'Voter with id ' + voterData['id'] + 'is already in the election'
                }), content_type='application/json')
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')
        return HttpResponse(json.dumps({
                'success':True
                }), content_type='application/json')

    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        if request.FILES:
            return addVotersFile(request,election)
        else:
            return addVotersJson(request,election)
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
@csrf_exempt
def removeVoters(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        data = json.loads(request.body.decode('utf-8'))
        for voterData in data['voterList']:
            try:
                Voter.objects.get(id=voterData['id'],election=election).delete()
            except Voter.DoesNotExist:
                pass
            except Exception as exception:
                return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')  
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
@csrf_exempt
def addQuestion(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        data = json.loads(request.body.decode('utf-8'))
        try:
            with transaction.atomic():
                for questionData in data['questionList']:
                    question = Question()
                    question.election = election
                    question.question = questionData['question']
                    question.save()
                    for answerData in questionData['answers']:
                        answer = Answer()
                        answer.answer = answerData
                        answer.save()
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')
        return HttpResponse(json.dumps({'success':True}), content_type='application/json')      
    else:
        return HttpResponseNotAllowed(['POST'])


'''from django.shortcuts import render,redirect
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
import requests

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

@login_required
def register(request,election_id):
    try:
        election = Election.objects.get(uuid=election_id)
    except Election.DoesNotExist:
        raise Http404("Election does not exist")
    voter = election.eligiblevoter_set.all().filter(voterId=request.user.username).first()
    if voter:
        if request.method == 'GET':
            r = request.json('127.0.0.1:8001/createCredentials/',json={
                'electionId':election_id,
                'voterId':voter.voterId,
                'email':voter.email})
            if r.status != 200:
                return HttpResponse(json.dumps({'error':r.status}),content_type='application/json')
            else:
                r.json()
                return HttpResponse(json.dumps({'success':True}),content_type='application/json')

@login_required
def cast(request,election_id):
     try:
        election = Election.objects.get(uuid=election_id)
    except Election.DoesNotExist:
        raise Http404("Election does not exist")
    voter = election.eligiblevoter_set.all().filter(voterId=request.user.username).first()
    if voter:
        if request.method == 'GET':
            payload = {}
            for question in election.question_set.all():
                payload[question] = question.answer_set.all()
            return HttpResponse(json.dumps(payload),content_type='application/json')
        else:
            
'''

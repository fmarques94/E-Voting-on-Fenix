#Core
import json
import requests
import csv
import requests
import datetime

#Django
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core import serializers
from django.http import HttpResponse, HttpResponseNotAllowed, Http404, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db import transaction
from django.conf import settings

#Models
from ElectionServer.models import Election 
from ElectionServer.models import Trustee
from ElectionServer.models import Voter
from ElectionServer.models import Question
from ElectionServer.models import Answer
from ElectionServer.models import Ballot

#Crypto
from ElectionServer.Crypto.ParameterGenerator import generate_parameters

def home(request):
    context = {'elections': Election.objects.all()}
    return render(request,'home.html',context)

def login(request):
    return render(request,'login.html')

def getElections(request):
    if request.method == 'GET':
        data = serializers.serialize('json',list(Election.objects.all()))
        return HttpResponse(data,content_type='application/json')
    else:
        return HttpResponseNotAllowed(['GET'])

@login_required
@csrf_exempt
def createElection(request):

    #@csrf_exempt
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
                'id':str(election.id)
                }),content_type='application/json')
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')
    
    if request.method == 'POST':
        return postCreateElection(request)
    else:
        return HttpResponseNotAllowed(['POST'])

#########################################################################################################################

@login_required
@csrf_exempt
def addTrustees(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
            if request.user != election.admin:
                return HttpResponseForbidden("Access denied")
            if datetime.now() >= election.startDate:
                return HttpResponse(json.dumps({'error':'The election has already started. Cannot add trustees now.'}),
             content_type='application/json', status=404)
            data = json.loads(request.body.decode('utf-8'))
            with transaction.atomic():
                for trusteeData in data['trusteeList']:
                    trustee = Trustee()
                    trustee.election = election
                    trustee.identifier = trusteeData['id']
                    trustee.name = trusteeData['name']
                    trustee.email = trusteeData['email']
                    trustee.save()
            return HttpResponse(json.dumps({'success':True}),content_type='application/json') 
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        except IntegrityError:
            return HttpResponse(json.dumps({'error':'Trustee '+ trusteeData['id'] + ' already present'})
            , content_type='application/json', status=404)
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
        if datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot remove trustees now.'}),
             content_type='application/json', status=404)
        try:
            data = json.loads(request.body.decode('utf-8'))
            for trusteeData in data['trusteeList']:
                Trustee.objects.get(identifier=trusteeData['id'],election=election).delete()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json')
        except Trustee.DoesNotExist:
            pass
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')  
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def getTrustees(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        data = serializers.serialize('json',list(Trustee.objects.all().filter(election=election)))
        return HttpResponse(data,content_type='application/json')
    else:
        return HttpResponseNotAllowed(['GET'])

######################################################################################################################

@login_required
def addVoters(request,election_id):

    def addVotersFile(request,election):
        try:
            csvfile = request.FILES['voters']
            reader = csv.reader(csvfile.read().decode('utf-8-sig').split('\n'),delimiter=";")
            with transaction.atomic():
                for row in reader:
                    if(len(row)>0):
                        voter = Voter()
                        voter.election = election
                        voter.identifier = row[0]
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
        try:
            data = json.loads(request.body.decode('utf-8'))
            with transaction.atomic():
                for voterData in data['voterList']:
                    voter = Voter()
                    voter.election = election
                    voter.identifier = voterData['id']
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
        if datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot add voters now.'}),
             content_type='application/json', status=404)
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
        if datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot remove voters now.'}),
             content_type='application/json', status=404)
        try:
            data = json.loads(request.body.decode('utf-8'))
            for voterData in data['voterList']:
                    Voter.objects.get(id=voterData['id'],election=election).delete()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json') 
        except Voter.DoesNotExist:
            pass
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')  
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def getVoters(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        data = serializers.serialize('json',list(Voter.objects.all().filter(election=election)))
        return HttpResponse(data,content_type='application/json')
    else:
        return HttpResponseNotAllowed(['GET'])

####################################################################################################################

@login_required
@csrf_exempt
def addQuestions(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        if datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot add questions now.'}),
             content_type='application/json', status=404)
        try:
            data = json.loads(request.body.decode('utf-8'))
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

@login_required
@csrf_exempt
def removeQuestions(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        if datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot remove questions now.'}),
             content_type='application/json', status=404)
        try:
            data = json.loads(request.body.decode('utf-8'))
            for questionData in data['questionList']:
                Question.objects.get(id=questionData['id'],election=election).delete()
        except Question.DoesNotExist:
            pass
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')
        return HttpResponse(json.dumps({'success':True}), content_type='application/json')      
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def getQuestions(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        data = serializers.serialize('json',list(Question.objects.all().filter(election=election)))
        return HttpResponse(data,content_type='application/json')
    else:
        return HttpResponseNotAllowed(['GET'])

#############################################################################################################################
@login_required
def register(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        try:
            voter = Voter.objects.get(identifier=request.user,election=election)
        except Voter.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Voter is not eligible for this election'}),
             content_type='application/json', status=404)
        if datetime.now() >= election.endDate:
            return HttpResponse(json.dumps({'error':'The election has ended'}),
             content_type='application/json', status=404)
        payload = {
            'election':election.id,
            'electionName': election.name,
            'cryptoParameters':election.cryptoParameters,
            'voter':voter.identifier,
            'email':voter.email,
        }
        r = requests.json(settings.CREDENTIAL_AUTHORITY,json=payload)
        if r.status!=200:
            return HttpResponse(json.dumps({'error':r.status}),content_type='application/json')
        data = json.loads(r.json())
        try:
            voter.publicCredential = data['publicCredential']
            voter.save()
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')
        return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json')
    else:
        return HttpResponseNotAllowed(['GET'])

##############################################################################################################################
@login_required
@csrf_exempt
def cast(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        try:
            voter = Voter.objects.get(identifier=request.user,election=election)
        except Voter.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Voter is not eligible for this election'}),
             content_type='application/json', status=404)
        if datetime.now() <= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has not started'}),
             content_type='application/json', status=404)
        if datetime.now() >= election.endDate:
            return HttpResponse(json.dumps({'error':'The election has ended'}),
             content_type='application/json', status=404)
        if election.openCastTime!=None and election.closeCastTime!=None:
            if datetime.now().time() <= election.openCastTime and datetime.now().time() >= election.closeCastTime:
                return HttpResponse(json.dumps({'error':'The ballot box is closed between ' + election.openCastTime + ' and '
                + election.closeCastTime}),
             content_type='application/json', status=404)
        data = json.loads(request.body.decode('utf-8'))
        try:
            if voter.publicCredential!=data['publicCredential']:
                return HttpResponse(json.dumps({'error':'Invalid public credential for voter with id ' + voter.identifier}),content_type='application/json', status=404)
            ballot = Ballot.objects.get(election=election,publicCredential=voter.publicCredential)
            return HttpResponse(json.dumps({'error':'The voter with id ' + voter.identifier + ' has already cast a ballot'}),
            content_type='application/json', status=404)
        except Ballot.DoesNotExist:
            #TODO verify ZK-proofs
            try:
                ballot = Ballot()
                ballot.publicCredential = voter.publicCredential
                ballot.ballot = data['ballot']
                ballot.save()
            except Exception as exception:
                return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json')
            return HttpResponse(json.dumps({
                    'success':True
                    }),content_type='application/json')
    else:
        return HttpResponseNotAllowed(['POST'])

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
def manageTrustees(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        #TODO
    else:
        return HttpResponseNotAllowed(['GET'])

@login_required
def manageVoters(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        #TODO
    else:
        return HttpResponseNotAllowed(['GET'])

@login_required
def manageQuestions(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        #TODO
    else:
        return HttpResponseNotAllowed(['GET'])


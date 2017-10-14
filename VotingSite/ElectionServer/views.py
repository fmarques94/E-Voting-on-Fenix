#Core
import json
import requests
import csv
import requests
import datetime
import secrets
import ast
import hashlib
import base64

#Django
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core import serializers
from django.http import HttpResponse, HttpResponseNotAllowed, Http404, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db import transaction, IntegrityError
from django.conf import settings
from django.urls import reverse

#Models
from ElectionServer.models import Election 
from ElectionServer.models import Trustee
from ElectionServer.models import Voter
from ElectionServer.models import Question
from ElectionServer.models import Answer
from ElectionServer.models import Ballot

#Crypto
from ElectionServer.Crypto.ParameterGenerator import generate_parameters
from ElectionServer.Crypto import Schnorr


#
# Method: GET
# Function: Renders home page. If the user is a authorized admin then the create election button is also rendered.
#
def home(request):
    return render(request,'home.html',{'admin':str(request.user) in settings.AUTHORIZED_ADMINS})
#
# Method: GET
# Function: Makes connection with Oauth in order to allow login through Fenix.
#
def login(request):
    return render(request,'login.html')

#
# Method: GET
# Function: Displays a list of all elections, taking a user to the bulletin board.
#
def elections(request):
    context = {'elections': Election.objects.all()}
    return render(request,'elections.html',context)

#
# Method: GET
# Function: Displays a list of all elections the user can manage, taking him to the management page.
#
@login_required
def manageElections(request):
    context = {'elections': Election.objects.filter(admin=request.user)}
    return render(request,'manageElections.html',context)

#
# Method: GET
# Function: Returns a JSON with all elections.
#
def getElections(request):
    if request.method == 'GET':
        data = serializers.serialize('json',list(Election.objects.all()))
        return HttpResponse(data,content_type='application/json')
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Method: GET
# Function: Return a page with a form for the creation of the election
# Method: POST
# Function: Receives a json with the name, description, a boolean which dictates if there are going to be paper votes,
#two dateTime which correspond to the start and end date of the election and optionally two times which correspond to
#the time which the Ballot Box can be open. It creates the election cryptographic parameters and a uuid which identifies
#the election. It also informs the credential authority of the new election which was created. If something goes wrong 
#it responds with a error 500. If everything goes well, it saves the data in the database and responds with a sucess 200.
#

@login_required
@csrf_exempt
def createElection(request):

    #@csrf_exempt
    def postCreateElection(request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            with transaction.atomic():    
                election = Election()
                election.name = data['name']
                election.description = data['description']
                election.hybrid = data['paperVotes']
                election.startDate = data['startDate']
                election.endDate = data['endDate']
                if datetime.datetime.strptime(data['startDate'],'%Y-%m-%d %H:%M') < datetime.datetime.now():
                    return HttpResponse(json.dumps({'error':'The election date is in the past.'})
                , content_type='application/json', status=406) 
                if election.endDate <= election.startDate:
                    return HttpResponse(json.dumps({'error':'The election end date must be greater than the election start date.'})
                , content_type='application/json', status=406) 
                if 'openCastTime' in data.keys():
                    election.openCastTime = data['openCastTime']
                    election.closeCastTime = data['closeCastTime']
                election.admin = request.user
                parameters = generate_parameters()
                election.cryptoParameters = {
                    "p":str(parameters['p']),
                    "q":str(parameters['q']),
                    "g":str(parameters['g'])
                }
                election.save()
                try:
                    r = requests.post(settings.CREDENTIAL_AUTHORITY+"/addElection/",data=json.dumps({'election':{'id':str(election.id),'endDate':election.endDate}}))
                except Exception as exception:
                    return HttpResponse(json.dumps({'error':"Failed connection to credential authority"}), content_type='application/json', status=500)
                if r.status_code!=200:
                    raise Exception('Got error code ' + str(r.status_code) + ' from registration server')
            return HttpResponse(json.dumps({
                'success':True,
                'currentUrl':reverse('createElection'),
                'redirectUrl':reverse('election',args=[str(election.id)])
                }),content_type='application/json')
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
    
    if request.method == 'POST':
        return postCreateElection(request)
    elif request.method == 'GET':
        return render(request,'createElection.html')
    else:
        return HttpResponseNotAllowed(['POST','GET'])

#
# Method: POST
# Function: Adds trustee to elections. Trustees cannot be added after the election has started.
# Receives a json with a list of dictionaries with the key trusteeList. Each dictionary
# has the id, name and email of the trustee. It receives the election_id trought the url. If the user who requested it is not the 
# election admin then it gives a forbidden error. In case the election does not exist it gives a 404 error. If the trustee is already
# present in the election it gives a 500 error which informs of such. Any other excepption is caught and sent as 500 error.
#

@login_required
@csrf_exempt
def addTrustees(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
            if request.user != election.admin:
                return HttpResponseForbidden("Access denied")
            if datetime.datetime.now() >= election.startDate:
                return HttpResponse(json.dumps({'error':'The election has already started. Cannot add trustees now.'}),
             content_type='application/json', status=500)
            data = json.loads(request.body.decode('utf-8'))
            with transaction.atomic():
                for trusteeData in data['trusteeList']:
                    t = Trustee()
                    t.election = election
                    t.identifier = trusteeData['id']
                    t.name = trusteeData['name']
                    t.email = trusteeData['email']
                    t.save()
            return HttpResponse(json.dumps({'success':True}),content_type='application/json') 
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        except IntegrityError:
            return HttpResponse(json.dumps({'error':'Trustee '+ trusteeData['id'] + ' already present'})
            , content_type='application/json', status=500)
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: POST
# Function: Removes trustees from the election. Trustees cannot be removed after the election has started and can only be 
# done so by the election admin. It receives a json with the list of ids of trustees with the key trusteeList. if a id doesn't
# correspond to a trustee it just ignores it, otherwise it removes it. Any other error is returned with error 500.
#
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
        if datetime.datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot remove trustees now.'}),
             content_type='application/json', status=500)
        try:
            data = json.loads(request.body.decode('utf-8'))
            for trusteeData in data['trusteeList']:
                Trustee.objects.get(identifier=trusteeData,election=election).delete()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json')
        except Trustee.DoesNotExist:
            pass
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)  
    else:
        return HttpResponseNotAllowed(['POST'])


#
# Method: GET
# Function: Return a Json with the information of all the trustees for a specific election. If the election does not exist
# it returns a 404 error.
#
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


#
# Method: POST
# Function: This can either receive a csv file or a json. This allows the possibility of adding a large number of voters
# using a csv. In case of Json it receives a list of dictionaries with the key voterList and each dictionary has the id and email
# of the voter. Similar the csv file has the id and email seperated by ;. In case of error the changes to the database are rolled back
# and the server responds with a 500. It also verifies that a voter is not added more than once. This can only be done by the
# election admin. It also only allows the addition on voters while the election does not begin.
#
@login_required
def addVoters(request,election_id):

    def addVotersFile(request,election):
        try:
            csvfile = request.FILES['csv']
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
                'error':'Voter with id ' + row[0] + ' is already in the election'
                }), content_type='application/json',status=500)
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
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
                'error':'Voter with id ' + voterData['id'] + ' is already in the election'
                }), content_type='application/json',status=500)
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
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
        if datetime.datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot add voters now.'}),
             content_type='application/json', status=500)
        if request.FILES:
            return addVotersFile(request,election)
        else:
            return addVotersJson(request,election)
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: POST
# Function: Removes voters from the election. Can only be done by the admin and before the election starts.
# It receives a json with a list with voter ids. The key of the list is voterList. If the voter does not exist it 
# simply ignores it. In case of error it responds with a error 500. 
#
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
        if datetime.datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot remove voters now.'}),
             content_type='application/json', status=500)
        try:
            data = json.loads(request.body.decode('utf-8'))
            for voterData in data['voterList']:
                Voter.objects.get(identifier=voterData,election=election).delete()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json') 
        except Voter.DoesNotExist:
            pass
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)  
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: GET
# Function: Return a list of voters for a specific election in json format.
#
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

#
# Method: POST
# Function: Adds questions and anwers to the election. This can only be done by the admin of the election and before the 
# election begins. If the election does not exist it returns a 404 error. It receives a json with a list of questions with
# the key questionList. This list contains a dictionary for each question with key question that has the question text and
# a list of answers with the key answers. For each answer and each question a uuid is created in order to identify these.
# The same question for a election or the same answer for a question is not allowed and the changes to the database are rollback.
# In case of error the server responds with a 500.
#
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
        if datetime.datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot add questions now.'}),
             content_type='application/json', status=500)
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
                        answer.question = question
                        answer.answer = answerData
                        answer.save()
        except IntegrityError:
            return HttpResponse(json.dumps({'error':"Cannot have duplicate question for the same election or duplicate answers for the same question"}), content_type='application/json', status=500) 
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
        return HttpResponse(json.dumps({'success':True}), content_type='application/json')      
    else:
        return HttpResponseNotAllowed(['POST'])
#
# Method: POST
# Function: Removes questions from the election. Can only be done by the admin and before the election begins.
# In case the question doesn't exist it just ignores the request. It receives a json with a list of the uuid of the questions.
# The answers for the question are deleted in cascade from the database. In case of error it responds with a 500.
#
#
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
        if datetime.datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot remove questions now.'}),
             content_type='application/json', status=404)
        try:
            data = json.loads(request.body.decode('utf-8'))
            for questionData in data['questionList']:
                Question.objects.get(id=questionData,election=election).delete()
        except Question.DoesNotExist:
            pass
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
        return HttpResponse(json.dumps({'success':True}), content_type='application/json')      
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: GET
# Function: Return a json representation of the questions and answers for a specific election.
#
@login_required
def getQuestions(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        data = getQuestionsAux(election)
        #data = serializers.serialize('json',list(Question.objects.all().filter(election=election)))
        return HttpResponse(json.dumps(data),content_type='application/json')
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Method: GET
# Function: Requests the credential authority for credentials. Can only be used by eligible voters.
# If the election doesn't exist or the request came from someone who isn't a voter it return a 404.
# Can only be done before the election ends and after the election starts. It send a post request to the 
# credential authority with a json containing the election id, the election name, the election cryptographic parameteres
# and the voter id and email. If the credential authority responds correctly it adds the public credential to the voter model,
# otherwise it responds with the same error as the credential authority. Any other error that occurs is responded with 500.
#
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
        if datetime.datetime.now() >= election.endDate or datetime.datetime.now()< election.startDate:
            return HttpResponse(json.dumps({'error':'The election is not currently running.'}),
             content_type='application/json', status=500)
        try:
            cryptoParameters = json.loads(election.cryptoParameters.replace('\'','"'))
            payload = {
                'election':str(election.id),
                'electionName': election.name,
                'cryptoParameters':{"p":cryptoParameters['p'],"g":cryptoParameters['g'],"q":cryptoParameters['q']},
                'voter':voter.identifier,
                'email':voter.email,
            }
            r = requests.post(settings.CREDENTIAL_AUTHORITY,data=json.dumps(payload))
            if r.status_code!=200:
                return HttpResponse(json.dumps({'error':str(r.status_code) + 'from credential Authority'}),content_type='application/json', status=r.status_code)
            data = r.json()
            voter.publicCredential = data['publicCredential']
            voter.save()
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
        return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json')
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Common: If the election doesn't exist or the user is not an eligible voter it responds with a 404 error.
# Method: GET
# Function: If the election is not running it responds with a closed ballot box. If the election has timed ballot boxes then
# it responds with a closed ballot box every time except between the correct interval. If the voter doesn't have a public credential
# it renders a register page where the voter can register to vote electronically. If the voter has the public credential the ballot box
# is rendered with all the information necessary in order to create the ballot even in offline mode. A group of random numbers are also generated
# and saved in order to compute the proofs of the ballot.
# Method: POST
# Function: Once again it verifies the time in order to see if it is legal to cast the vote. It verifies if 
# the ballots contains every question and a value for every answer of the election. It then checks the public credential
# received on the ballot and compares it with the public credential of the voter. It verifies every proof of the ballot and the 
# signature present. In case of failure in any of these it responds with a 500 error. Otherwise the ballot is saved.
# A ballot is formed as following: There are two main keys, the publicCredential that has the public credential of the voter
# and the ballot. The ballot is a dictionary where each key is the uuid of a question. The value with another dictionary with the key answer,
# and another with the overall_proof. In the answers there are dictionary with each key a uuid of the answer and in that the encrytion and individual answer.
#

@login_required
@csrf_exempt
def cast(request,election_id):
    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
    try:
        voter = Voter.objects.get(identifier=request.user,election=election)
    except Voter.DoesNotExist:
        return HttpResponse(json.dumps({'error':'Voter is not eligible for this election'}),
            content_type='application/json', status=404)
    if request.method == 'POST':
        if datetime.datetime.now() <= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has not started'}),
             content_type='application/json', status=404)
        if datetime.datetime.now() >= election.endDate:
            return HttpResponse(json.dumps({'error':'The election has ended'}),
            content_type='application/json', status=404)
        if election.openCastTime!=None and election.closeCastTime!=None:
            if datetime.datetime.now().time() <= election.openCastTime or datetime.datetime.now().time() >= election.closeCastTime:
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
                questions = getQuestionsAux(election)
                randoms = json.loads(voter.proofRandomValues)
                cryptoParameters = json.loads(election.cryptoParameters.replace('\'','"'))
                p = int(cryptoParameters['p'])
                q = int(cryptoParameters['q'])
                g = int(cryptoParameters['g'])
                h = int(election.publicKey,16)
                schnorr = Schnorr.Schnorr()
                schnorr.keys={
                "pub":{
                    "p":p,
                    "q":q,
                    "alpha":g,
                    "beta":int(data['publicCredential'])
                }}
                signMessage = 1
                for i,question in enumerate(questions["questionList"]):
                    if question["id"] not in data["ballot"]:
                        return HttpResponse(json.dumps({'error':'Ballot is not well formed'}), content_type='application/json', status=500)
                    questionData = data['ballot'][question["id"]]
                    totalAlpha = 1
                    totalBeta = 1
                    for j,answer in enumerate(question["answers"]):
                        if answer["id"] not in questionData["answers"]:
                            return HttpResponse(json.dumps({'error':'Ballot is not well formed'}), content_type='application/json', status=500)
                        answerData = questionData["answers"][answer["id"]]
                        alpha = int(answerData['alpha'])
                        beta = int(answerData['beta'])
                        totalAlpha = totalAlpha * alpha
                        totalBeta = totalBeta * beta
                        signMessage = signMessage*alpha*beta
                        random = int(randoms[question["id"]][answer["id"]])
                        if random == (int(answerData['individualProof'][0]['challenge']) + int(answerData['individualProof'][1]['challenge']))%p:
                            print(answerData['individualProof'][0])
                            proof0 = testProof(int(answerData['individualProof'][0]['challenge']),int(answerData['individualProof'][0]['response']),g,h,p,alpha,beta,0)
                            print(proof0)
                            print(answerData['individualProof'][1])
                            proof1 = testProof(int(answerData['individualProof'][1]['challenge']),int(answerData['individualProof'][1]['response']),g,h,p,alpha,beta,1)
                            print(proof1)
                            if int(answerData['individualProof'][0]['A'])==proof0[0] and int(answerData['individualProof'][0]['B'])==proof0[1] and int(answerData['individualProof'][1]['A'])==proof1[0] and int(answerData['individualProof'][1]['B'])==proof1[1]:
                                continue
                            else:
                                return HttpResponse(json.dumps({'error':'Proof verification failed.'}), content_type='application/json', status=500)
                        else:
                            return HttpResponse(json.dumps({'error':'Proof verification failed.'}), content_type='application/json', status=500)
                    random = int(randoms[question["id"]]["overall"])
                    if random == (int(questionData['overall_proof'][0]['challenge']) + int(questionData['overall_proof'][1]['challenge']))%p:
                        proof0 = testProof(int(questionData['overall_proof'][0]['challenge']),int(questionData['overall_proof'][0]['response']),g,h,p,totalAlpha,totalBeta,0)
                        proof1 = testProof(int(questionData['overall_proof'][1]['challenge']),int(questionData['overall_proof'][1]['response']),g,h,p,totalAlpha,totalBeta,1)
                        if int(questionData['overall_proof'][0]['A'])==proof0[0] and int(questionData['overall_proof'][0]['B'])==proof0[1] and int(questionData['overall_proof'][1]['A'])==proof1[0] and int(questionData['overall_proof'][1]['B'])==proof1[1]:
                            continue
                        else:
                            return HttpResponse(json.dumps({'error':'Proof verification failed.'}), content_type='application/json', status=500)
                    else:
                        return HttpResponse(json.dumps({'error':'Proof verification failed.'}), content_type='application/json', status=500)
                signMessage = signMessage%p
                if not schnorr.verify([int(data['ballot']['signature'][0]),int(data['ballot']['signature'][1])],signMessage):
                    return HttpResponse(json.dumps({'error':"Failed signature verification"}), content_type='application/json', status=500)
                ballot = Ballot()
                ballot.election = election
                ballot.publicCredential = voter.publicCredential
                ballot.ballot = data['ballot']
                ballot.SBT = hashlib.sha256(request.body).hexdigest()
                ballot.save()
            except Exception as exception:
                return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
            return HttpResponse(json.dumps({
                    'success':True
                    }),content_type='application/json')
    elif request.method == 'GET':
        if voter.publicCredential:
            if datetime.datetime.now() <= election.startDate:
                return render(request,"closedBallotBox.html",{'election':election})
            if datetime.datetime.now() >= election.endDate:
                return render(request,"closedBallotBox.html",{'election':election})
            if election.openCastTime!=None and election.closeCastTime!=None:
                if datetime.datetime.now().time() <= election.openCastTime or datetime.datetime.now().time() >= election.closeCastTime:
                    return render(request,"closedBallotBox.html",{'election':election})
            try:
                ballot = Ballot.objects.get(election=election,publicCredential=voter.publicCredential)
                return render(request,"closedBallotBox.html",{'election':election})
            except Ballot.DoesNotExist:
                cryptoParameters = json.loads(election.cryptoParameters.replace('\'','"'))
                questions = getQuestionsAux(election)
                randoms = {}
                for question in questions["questionList"]:
                    randoms[question["id"]] = {}
                    randoms[question["id"]]["overall"] = str(secrets.randbelow(int(cryptoParameters['p'])))
                    for answer in question["answers"]:
                        randoms[question["id"]][answer["id"]] = str(secrets.randbelow(int(cryptoParameters['p'])))
                voter.proofRandomValues = json.dumps(randoms)
                voter.save()
                return render(request,"ballotBox.html",{'election':election,'questions':json.dumps(questions),'randoms':json.dumps(randoms)})
        else:
            if datetime.datetime.now() >= election.endDate or datetime.datetime.now() <= election.startDate:
                return render(request,"closedBallotBox.html",{'election':election})
            if election.publicKey:
                return render(request,"register.html",{'election':election,'email':voter.email})
            else:
                return HttpResponse(json.dumps({'error':'Election does not have a public key.'}), content_type='application/json', status=404)
    else:
        return HttpResponseNotAllowed(['GET','POST'])

#
# Auxiliary function to calculate the proof parameters
#
def testProof(challenge,response,g,h,p,alpha,beta,message):
    A = (pow(g,response,p)*pow(pow(alpha,p-2,p),challenge,p))%p
    B = (pow(h,response,p) * pow(pow(beta,p-2,p),challenge,p) * pow(g,(message*challenge),p))%p
    return A,B

#
# Method: GET
# Function: Render the page of the management of the election. if the election has ended then a button to manage the tally is 
# also rendered.
#
@login_required
def election(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        if request.user == election.admin:
            endOfElection = False
            if datetime.datetime.now() >= election.endDate:
                endOfElection = True
            return render(request,'manageElection.html',{'election':election,'endOfElection':endOfElection})
        else:
            return HttpResponseForbidden("Access denied")
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Method: GET
# Function: Renders the page to manage the trustees. Also displays a lisr of the trustees and their key share.
# This page also allows the admin to aggregate the public key
#
@login_required
def manageTrustees(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        keyshares = {}
        for t in Trustee.objects.filter(election=election):
            if t.publicKeyShare:
                if 'pk' in json.loads(t.publicKeyShare.replace('\'','"')):
                    keyshares[t.identifier] = json.loads(t.publicKeyShare.replace('\'','"'))
                    keyshares[t.identifier]["proof"]["e"] = t.keyShareProofRandom
        return render(request,'manageTrustees.html',{'election':election,'keyShares': keyshares})
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Method: GET
# Function: Renders the page to manage the voters. It also displays a list of all the eligible voters.
#
@login_required
def manageVoters(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        return render(request,'manageVoters.html',{'election':election})
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Method:GET
# Function: Renders the page to manage the questions. It also displays a list of all the questions and answers.
#
@login_required
def manageQuestions(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        return render(request,'manageQuestions.html',{'election':election})
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Method: GET
# Function: Renders the page for the trustees to generate a key share and to partial decrypt the tally depending on the stage of
# the election.
# Method: POST
# Function: Allows the trustee to input a key share for the key generation protocol.
#
@login_required
def trustee(request,election_id):

    def getMethodTrustee(election,t):
        if datetime.datetime.now() < election.startDate:
            try:
                if not t.keyShareProofRandom:
                    t.keyShareProofRandom = str(secrets.randbelow(int(ast.literal_eval(election.cryptoParameters)['p'])))
                    t.save()
                    return render(request,'generateKeyShare.html',{'election':election,'trustee':t})
                else:
                    return render(request,'generateKeyShare.html',{'election':election,'trustee':t})
            except Exception as exception:
                return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
        elif datetime.datetime.now() > election.endDate and election.aggregatedEncTally:
            cryptoParams = json.loads(election.cryptoParameters.replace('\'','"'))
            questions = getQuestionsAux(election)
            if not t.partialDecryption:
                randoms = {}
                for question in questions["questionList"]:
                    randoms[question["id"]] = {}
                    for answer in question["answers"]:
                        randoms[question["id"]][answer["id"]] = str(secrets.randbelow(int(cryptoParams['p'])))
                try:
                    t.decryptionProofRandom = json.dumps(randoms)
                    t.save()
                except:
                    return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
            return render(request,'partialDecrypt.html',{
                'election':election,
                'trustee':t,
                'aggregatedEncTally':election.aggregatedEncTally.replace("'",'"'),
                'p':cryptoParams['p'],
                'g':cryptoParams['g'],
                'randoms':json.dumps(t.decryptionProofRandom)})
        else:
            return render(request,'generateKeyShare.html',{'election':election,'trustee':t, 'started':True})

    def postMethodTrustee(election,t):
        if datetime.datetime.now() < election.startDate:
            if t.publicKeyShare:
                return HttpResponse(json.dumps({'error':'You have already generated a key share'}), content_type='application/json',status=500)
            else:
                data = json.loads(request.body.decode('utf-8'))
                if 'pk' in data:
                    t.publicKeyShare = data
                    try:
                        t.save()
                    except Exception as exception:
                        return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
                    return HttpResponse(json.dumps({'success':True}), content_type='application/json')
                else:
                    return HttpResponse(json.dumps({'error':'Bad json. Does not have necessary elements.'}), content_type='application/json',status=500)
        elif datetime.datetime.now() > election.endDate:
            return
        else:
            return HttpResponseForbidden("Access denied")

    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        raise Http404("Election does not exist")
    try:
        t = Trustee.objects.get(election=election,identifier=request.user)
    except Trustee.DoesNotExist:
        return HttpResponseForbidden("Access denied")
    if request.method == 'GET':
        return getMethodTrustee(election,t)
    elif request.method == 'POST':
        return postMethodTrustee(election,t)
    else:
        return HttpResponseNotAllowed(['GET','POST'])

#
# Method: GET
# Function: Renders a list of all the elections where the user is a trustee.
#
@login_required
def trusteeElectionList(request):
    if request.method == 'GET':
        t = Trustee.objects.filter(identifier=request.user)
        return render(request,'trusteeElectionList.html',{'trustee':t})
    else:
        return HttpResponseNotAllowed(['GET'])
#
# Method: POST
# Function: Allows for the election admin to post the election public key. It can only be accessed before the election starts
# It receives a json with a key pk whose value is the public key.
#
@login_required
def addElectionPublicKey(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        if election.admin!=request.user:
            return HttpResponseForbidden("Access denied")
        if datetime.datetime.now() >= election.startDate:
            return HttpResponse(json.dumps({'error':'The election has already started. Cannot set the public key.'}),
             content_type='application/json', status=404)
        if election.publicKey:
            return HttpResponse(json.dumps({'error':'The election already has a public key'}),
             content_type='application/json', status=404)
        try:
            data = json.loads(request.body.decode('utf-8'))
            if 'pk' in data:
                election.publicKey = data['pk']
                election.save()
                return HttpResponse(json.dumps({'sucess':True}),
             content_type='application/json')
            else:
                return HttpResponse(json.dumps({'error':'The json is not well formed.'}),
             content_type='application/json', status=404)
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: GET
# Function: Renders the bulletin board. Here voters can check for the election information, can check their SBT and the trustees
# public key share.
#
@login_required
def bulletinBoard(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        keyshares = {}
        for t in Trustee.objects.filter(election=election):
            if t.publicKeyShare:
                if 'pk' in json.loads(t.publicKeyShare.replace('\'','"')):
                    keyshares[t.identifier] = json.loads(t.publicKeyShare.replace('\'','"'))
        voters = {}
        for voter in Voter.objects.filter(election=election):
            if voter.paperVoter:
                voters[voter.identifier] = "paper Voter"
                continue
            if voter.publicCredential:
                try:
                    ballot = Ballot.objects.get(election=election,publicCredential=voter.publicCredential)
                    voters[voter.identifier] = ballot.SBT
                except Ballot.DoesNotExist:
                    voters[voter.identifier] = ""
            else:
                voters[voter.identifier] = ""
        tally = None
        if election.tally:
            tally = json.loads(election.tally.replace("'",'"'))
        return render(request,'bulletinBoard.html',{
            'election':election,
            'keyShares':keyshares,
            'voters':voters,
            'tally':tally,
            'eligibleVoter':str(request.user) in voters.keys()
            })
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Method: GET
# Function: Renders the page which allows to audit a ballot. It passes all the information necessary in order for the audit
# to run offline if needed.
#
@login_required
def auditBallot(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        questions = getQuestionsAux(election)
        try:
            voter = Voter.objects.get(identifier=request.user,election=election)
        except Voter.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Voter is not eligible for this election'}),
                content_type='application/json', status=404)
        randoms = voter.proofRandomValues
        if randoms:
            return render(request,"auditBallot.html",{'election':election,'questions':json.dumps(questions),'randoms':randoms})
        else:
            return HttpResponse(json.dumps({'error':'Voter didn\'t access ballot box to create a ballot'}),
                content_type='application/json', status=404)
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Auxiliary function which return a dictionary with all the questions and answers of an election, including their ids.
#
def getQuestionsAux(election):
    data = {"questionList":[]}
    for question in Question.objects.all().filter(election=election):
        questionData = {}
        questionData["id"] = str(question.id)
        questionData["question"] = question.question
        questionData["answers"] = []
        for answer in Answer.objects.all().filter(question=question):
            questionData["answers"].append({
                "id":str(answer.id),
                "answer":answer.answer
                })
        data["questionList"].append(questionData)
    return data
#
# Method: GET
# Function: Renders the page in order to manage the tally. if the election has paper votes it first request that the admin
# input the paper voters and paper results. After that, or if it didn't have paper votes, the admin can create the aggregated encrypted tally.
# Finally after all the trustees have made their partial decryptions it allows the admin to aggregate these a publish them.
# This is only accessible after the election has ended.
#
@login_required
def manageTally(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise Http404("Election does not exist")
        if request.user == election.admin:
            if datetime.datetime.now() >= election.endDate:
                paperVoters = Voter.objects.filter(election=election,paperVoter=True)
                paperVotersIdentifiers = paperVoters.values_list('identifier', flat=True)
                paperVoterCredentials = paperVoters.values_list('publicCredential', flat=True)
                ballots = []
                numberOfEBallots = 0
                for b in Ballot.objects.filter(election=election).exclude(publicCredential__in=paperVoterCredentials).values_list('ballot', flat=True):
                    ballots.append(json.loads(b.replace('\'','"')))
                    numberOfEBallots+=1
                finalEBallots = json.dumps({"ballotList":ballots})
                cryptoParameters = json.loads(election.cryptoParameters.replace('\'','"'))
                trustees = Trustee.objects.filter(election=election)
                partialDecryptions = {"partialDecryptionList":[]}
                numberOfPartialeDecryptions = 0
                for t in trustees:
                    if t.partialDecryption:
                        p = json.loads(t.partialDecryption.replace('\'','"'))
                        p["publicKeyShare"] = json.loads(t.publicKeyShare.replace('\'','"'))
                        p["randoms"] = json.loads(t.decryptionProofRandom.replace('\'','"'))
                        partialDecryptions["partialDecryptionList"].append(p)
                        numberOfPartialeDecryptions+=1
                return render(request,'manageTally.html',{
                    'election':election,
                    'paperVoters':paperVotersIdentifiers,
                    'questions':json.dumps(getQuestionsAux(election)),
                    #'finalBallots':finalEBallots,
                    'p':cryptoParameters['p'],
                    'g':cryptoParameters['g'],
                    'trustees':trustees,
                    'partialDecryptions':json.dumps(partialDecryptions),
                    'numberOfEBallots':numberOfEBallots,
                    'ready':numberOfPartialeDecryptions == len(trustees.values_list('publicKeyShare', flat=True))
                })
            else:
                return HttpResponseForbidden("Election has not yet ended. Cannot manage tally without election ending.")
        else:
            return HttpResponseForbidden("Access denied")
    else:
        return HttpResponseNotAllowed(['GET'])

#
# Method: POST
# Function: Works similiar to how we add the eligible voters. The request now only needs the ids. And can only be accessed 
# when the election has ended.
#
@login_required
def addPaperVoters(request,election_id):

    def addPaperVotersFile(request,election):
        try:
            csvfile = request.FILES['csv']
            reader = csv.reader(csvfile.read().decode('utf-8-sig').split('\n'),delimiter=";")
            with transaction.atomic():
                for row in reader:
                    if(len(row)>0):
                        voter = Voter.objects.get(identifier=row[0],election=election)
                        voter.paperVoter = True
                        voter.save()
        except Voter.DoesNotExist:
            return HttpResponse(json.dumps({
                'error':'Voter with id ' + row[0] + 'is not an eligible voter.'
                }), content_type='application/json',status=500)
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
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
        if datetime.datetime.now() <= election.endDate:
            return HttpResponse(json.dumps({'error':'The election has not ended. Cannot add paper voters yet!'}),
             content_type='application/json', status=404)
        if request.FILES:
            return addPaperVotersFile(request,election)
        else:
            return HttpResponse(json.dumps({'error':'No file submited'}),
             content_type='application/json', status=404)
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: POST
# Function: Works in a similiar way to the remove of eligible voters.
#
@login_required
@csrf_exempt
def removePaperVoters(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        if datetime.datetime.now() <= election.endDate:
            return HttpResponse(json.dumps({'error':'The election has not ended. Cannot manage paper voters.'}),
             content_type='application/json', status=404)
        try:
            data = json.loads(request.body.decode('utf-8'))
            for voterData in data['voterList']:
                voter = Voter.objects.get(identifier=voterData,election=election)
                voter.paperVoter = False
                voter.save()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json') 
        except Voter.DoesNotExist:
            pass
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)  
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: POST
# Function: Receives the paper results of the election. The json keys are made up of the questions and answers uuid.
# If the number of paper votes doesn't add up with the number of votes for each question then a error is returned.
# This function can only be accessed at the end of the election and by the administrator. 
#
@login_required
def submitPaperResults(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        if datetime.datetime.now() <= election.endDate:
            return HttpResponse(json.dumps({'error':'The election has not ended. Cannot submit paper voting results.'}),
             content_type='application/json', status=404)
        try:
            data = json.loads(request.body.decode('utf-8'))
            questions = getQuestionsAux(election)
            for i,question in enumerate(questions['questionList']):
                if question['id'] not in data.keys():
                    return HttpResponse(json.dumps({'error':'Incomplete Results.'}), content_type='application/json', status=500)
                for answer in questions['questionList'][i]['answers']:
                    if answer["id"] not in data[question['id']].keys():
                        return HttpResponse(json.dumps({'error':'Incomplete Results.'}), content_type='application/json', status=500)
            numberOfPaperVoters = len(Voter.objects.filter(election=election,paperVoter=True))
            for question in data:
                numberOfPaperVotes = 0
                for answer in data[question]:
                    numberOfPaperVotes = numberOfPaperVotes + int(data[question][answer])
                if numberOfPaperVoters!=numberOfPaperVotes:
                    return HttpResponse(json.dumps({'error':'Number of paper votes and voters doesn\'t match. Please review them'}), content_type='application/json', status=500)
            election.paperResults = data
            election.save()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json') 
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: POST
# Function: Allows each of the trustees to submit a partial decryption. This can only be done after the election has ended
# if an aggregated encrypted tally has been computed and if the trustee participated in the election key generation protocol.
#
@login_required
def submitPartialDecryption(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        try:
            t = Trustee.objects.get(election=election,identifier=request.user)
        except Trustee.DoesNotExist:
            return HttpResponseForbidden("Access denied")
        if datetime.datetime.now() <= election.endDate:
            return HttpResponse(json.dumps({'error':'The election has not ended. Cannot submit partial decryption.'}),
             content_type='application/json', status=404)
        if not t.publicKeyShare:
            return HttpResponse(json.dumps({'error':'Trustee didn\'t participate in the protocol'}), content_type='application/json', status=500)
        if not election.aggregatedEncTally:
            return HttpResponse(json.dumps({'error':'Trustee cannot submit decryption without aggregated tally'}), content_type='application/json', status=500)
        data = json.loads(request.body.decode('utf-8'))
        questions = getQuestionsAux(election)
        for question in questions["questionList"]:
            if question["id"] not in data.keys():
                return HttpResponse(json.dumps({'error':'Partial Decryption not well formed.'}), content_type='application/json', status=500)
            for answer in question["answers"]:
                if answer["id"] not in data[question["id"]].keys():
                    return HttpResponse(json.dumps({'error':'Partial Decryption not well formed.'}), content_type='application/json', status=500)
        try:
            t.partialDecryption = data
            t.save()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json')
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: POST
# Function: Allows for the administator to publish the election results. Can only be accessed at the end of the election.
# the published results must contain an id for each question and answer and the total number of votes must be equal to ~
# the number of paper voters and the number of e-ballots of non paper votes.
#
@login_required
def publishResults(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        if datetime.datetime.now() <= election.endDate:
            return HttpResponse(json.dumps({'error':'The election has not ended. Cannot submit election tally.'}),content_type='application/json', status=404)
        try:
            data = json.loads(request.body.decode('utf-8'))
            paperVoters = Voter.objects.filter(election=election,paperVoter=True)
            paperVoterCredentials = paperVoters.values_list('publicCredential', flat=True)
            NumberEVoters = Ballot.objects.filter(election=election).exclude(publicCredential__in=paperVoterCredentials) 
            questions = getQuestionsAux(election)
            for question in questions["questionList"]:
                numberOfVotes = 0
                if question["id"] not in data.keys():
                    return HttpResponse(json.dumps({'error':'Results not well formed.'}), content_type='application/json', status=500)
                for answer in question["answers"]:
                    if answer["id"] not in data[question["id"]][1].keys():
                        return HttpResponse(json.dumps({'error':'Results not well formed.'}), content_type='application/json', status=500)
                    numberOfVotes = numberOfVotes + int(data[question["id"]][1][answer["id"]][1])
                if (len(NumberEVoters)+len(paperVoters))!=numberOfVotes:
                    return HttpResponse(json.dumps({'error':'Results are invalid. Different number of voters and votes'}), content_type='application/json', status=500)
            election.tally = data
            election.save()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json')
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: POST
# Function: Deletes an election. Can only be accessed by the election administrator. This deletes the election and all the data
# which belongs to it.
#
@login_required
def deleteElection(request,election_id):
    if request.method == 'POST':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        try:
            election.delete()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json')
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json', status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

#
# Method: GET
# Function: Aggregates the encrypted tally.
#

@login_required
def aggregateEncTally(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if request.user != election.admin:
            return HttpResponseForbidden("Access denied")
        if datetime.datetime.now() >= election.endDate:
            paperVoters = Voter.objects.filter(election=election,paperVoter=True)
            paperVoterCredentials = paperVoters.values_list('publicCredential', flat=True)
            ballots = []
            numberOfEBallots = 0
            for b in Ballot.objects.filter(election=election).exclude(publicCredential__in=paperVoterCredentials).values_list('ballot', flat=True):
                ballots.append(json.loads(b.replace('\'','"')))
                numberOfEBallots+=1
            questions = getQuestionsAux(election)
            result = {}
            p = int(json.loads(election.cryptoParameters.replace('\'','"'))["p"])
            for question in questions["questionList"]:
                result[question['id']] = {}
                for answer in question["answers"]:
                    for ballot in ballots:
                        ballotAnswer = ballot[question["id"]]["answers"][answer["id"]]
                        if answer["id"] in result[question['id']]:
                            alpha = result[question['id']][answer['id']]["alpha"]
                            beta = result[question['id']][answer['id']]["beta"]
                            aux = {
                                "alpha": (alpha*int(ballotAnswer['alpha']))%p,
                                "beta": (beta*int(ballotAnswer['beta']))%p
                            }
                        else:
                            aux = {
                                "alpha": int(ballotAnswer['alpha']),
                                "beta": int(ballotAnswer['beta'])
                            }
                        result[question['id']][answer['id']] = aux
                    result[question['id']][answer['id']]["alpha"] = str(result[question['id']][answer['id']]["alpha"])
                    result[question['id']][answer['id']]["beta"] = str(result[question['id']][answer['id']]["beta"])
            election.aggregatedEncTally = json.dumps(result)
            election.save()
            return HttpResponse(json.dumps({
                'success':True
                }),content_type='application/json')
        else:
            return HttpResponseForbidden("Election has not yet ended. Cannot manage tally without election ending.")
    else:
        return HttpResponseNotAllowed(['GET'])


#
# Method: GET
# Function: Exports data at the end of the election in order for the voters to do the verification.
#

def exportData(request,election_id):
    if request.method == 'GET':
        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            return HttpResponse(json.dumps({'error':'Election does not exist'}), content_type='application/json', status=404)
        if election.tally:
            export = {}
            electionExport = {}
            electionExport['uuid'] = str(election.id)
            electionExport['name'] = election.name
            electionExport['CryptoParameters'] = json.loads(election.cryptoParameters.replace('\'','"'))
            electionExport['ElectionPublicKey'] = election.publicKey
            electionExport['questions'] = getQuestionsAux(election)
            electionExport['aggregatedEncryptedTally'] = json.loads(election.aggregatedEncTally)
            trusteesExport = {}
            for t in Trustee.objects.filter(election=election):
                if t.publicKeyShare:
                    if 'pk' in json.loads(t.publicKeyShare.replace('\'','"')):
                        trusteesExport[t.identifier] = {}
                        trusteesExport[t.identifier]['KeyShare'] = json.loads(t.publicKeyShare.replace('\'','"'))
                        trusteesExport[t.identifier]['KeyShare']["proof"]["e"] = t.keyShareProofRandom
                        trusteesExport[t.identifier]['PartialDecryptions'] = json.loads(t.partialDecryption.replace('\'','"'))
                        trusteesExport[t.identifier]['PartialDecryptionsRandom'] = json.loads(t.decryptionProofRandom.replace('\'','"'))
            ballotsExport = {}
            paperVoters = Voter.objects.filter(election=election,paperVoter=True)
            paperVoterCredentials = paperVoters.values_list('publicCredential', flat=True)
            numberOfEBallots = 0
            for b in Ballot.objects.filter(election=election).exclude(publicCredential__in=paperVoterCredentials):
                ballotsExport[b.publicCredential] = {}
                ballotsExport[b.publicCredential]['ballotData'] = json.loads(b.ballot.replace('\'','"'))
                ballotsExport[b.publicCredential]['SBT'] = b.SBT            
            export['election'] = electionExport
            export['trusteesData'] = trusteesExport
            export['ballotExport'] = ballotsExport
            response = HttpResponse(json.dumps(export), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export.json'
            return response
        else:
            return HttpResponse(json.dumps({'error':'Election doesn\'t have the results publishes yet!'}), content_type='application/json', status=404)
    else:
        return HttpResponseNotAllowed(['GET'])
#Core
import json

#Django
from django.http import HttpResponse,HttpResponseNotAllowed
from django.core.mail import send_mail,EmailMultiAlternatives
from django.db import transaction

#Models

from Registration.models import Election
from Registration.models import Credential


#Crypto
from Registration.Crypto import Schnorr

def createCredentials(request):
    if request.method=='POST':
        try:
            print(request.body)
            data = json.loads(request.body.decode('utf-8'))
            election = Election.objects.get(id=data['election'])
            s = Schnorr.Schnorr()
            while(True):
                keys = s.generate_keys({
                    'p':int(data['cryptoParameters']['p']),
                    'q':int(data['cryptoParameters']['q']),
                    'g':int(data['cryptoParameters']['g'])
                })
                try:
                    credential = Credential.objects.get(election=election,credential=str(keys['pub']['beta']))
                except Credential.DoesNotExist:
                    break
            with transaction.atomic():
                credential = Credential()
                credential.election = election
                credential.credential = str(keys['pub']['beta'])
                credential.save()

                #send_mail('Election Credentials: ' + data['electionName'],
                #'Voter ' + data['voter'] + ',\n'
                #'The credentials for the election are:\n'+
                #'Secret: ' + str(keys['priv']['a']) + '\n'+
                #'Public: ' + str(keys['pub']['beta']) + '\n',
                #'no-reply@tecnico.ulisboa.pt',
                #[data['email']],
                #fail_silently=False)

                subject, from_email, to = 'Election Credentials:'+ data['electionName'], 'no-reply@tecnico.ulisboa.pt', data['email']
                text_content = 'Voter ' + data['voter'] + ',\n The credentials for the election are:\n Secret: ' + str(keys['priv']['a']) + '\n Public: ' + str(keys['pub']['beta']) + '\n'
                html_content = '<p>Voter ' + data['voter'] + ',</p><p> The credentials for the election are:</p> <p style="word-break: break-all;">Secret: ' + str(keys['priv']['a']) + '</p> <p style="word-break: break-all;">Public: ' + str(keys['pub']['beta']) + '</p>'
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

            return HttpResponse(json.dumps({'publicCredential':str(keys['pub']['beta'])}),content_type='application/json')
        except Exception as exception:
            print(exception)
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json',status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

def addElection(request):
    if request.method=='POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(data["election"]["id"])
            print(data["election"]["endDate"])
            election = Election()
            election.id = data["election"]["id"]
            election.endDate = data["election"]["endDate"]
            election.save()
            return HttpResponse(json.dumps({"success":True}),content_type='application/json',status=200)
        except Exception as exception:
            print(exception)
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json',status=500)
    else:
        return HttpResponseNotAllowed(['POST'])
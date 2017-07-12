#Core
import json

#Django
from django.http import HttpResponse,HttpResponseNotAllowed
from django.core.mail import send_mail

#Crypto
from Registration.Crypto import Schnorr

def createCredentials(request):
    if request.method=='POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            s = Schnorr.Schnorr()
            keys = s.generate_keys({
                'p':int(data['cryptoParameters']['p']),
                'q':int(data['cryptoParameters']['q']),
                'g':int(data['cryptoParameters']['g'])
            })
            send_mail('Election Credentials: ' + data['electionName'],
            'Voter ' + data['voter'] + ',\n'
            'The credentials for the election are:\n'+
            'Secret: ' + str(keys['priv']['a']) + '\n'+
            'Public: ' + str(keys['pub']['beta']) + '\n',
            'no-reply@tecnico.ulisboa.pt',
            [data['email']],
            fail_silently=False)

            return HttpResponse(json.dumps({'publicCredential':str(keys['pub']['beta'])}),content_type='application/json')
        except Exception as exception:
            return HttpResponse(json.dumps({'error':repr(exception)}), content_type='application/json',status=500)
    else:
        return HttpResponseNotAllowed(['POST'])
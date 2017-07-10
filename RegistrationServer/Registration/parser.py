from Registration.models import Eletion, EVoter
from django.db.utils import IntegrityError
from django.http import HttpResponse
from Registration.Crypto import Schnorr

electionKeys = ('uuid','p','q','g')
eVoterKeys = ('electionId','id','email')

def parseElectionJson(jsonObject):
    if 'election' in jsonObject:
        if all(key in electionKeys for key in jsonObject['election']):
            try:
                election = Election()
                election.uuid = jsonObject['election']['uuid']
                election.p = jsonObject['election']['p']
                election.q = jsonObject['election']['q']
                election.g = jsonObject['election']['g']
                election.save()
                payload = {'success': True}
                return HttpResponse(json.dumps(payload),content_type='application/json')
            except IntegrityError:
                payload = {'error': 'Election already in server.'}
                response = HttpResponse(json.dumps(payload),content_type='application/json')
                response.status_code = 409
                return response
    payload = {'error': 'Json file does not contain all necessary information'}
    response = HttpResponse(json.dumps(payload),content_type='application/json')
    response.status_code = 400
    return response

def createCredentials(jsonObject):
    if all(key in eVoterKeys for key in jsonObject):
        try:
            try:
                election = Election.objects.get(uuid=jsonObject['electionId'])
            except Election.DoesNotExist:
                payload = {'error': 'Election with id ' + jsonObject['electionId'] + ' is not in the server'}
                response = HttpResponse(json.dumps(payload),content_type='application/json')
                response.status_code = 400
                return response
            voter = EVoter()
            voter.election = election
            voter.voterId = jsonObject['voterId']
            voter.email = jsonObject['email']
            voter.save()
        except IntegrityError:
            payload = {'error': 'Election already in server.'}
            response = HttpResponse(json.dumps(payload),content_type='application/json')
            response.status_code = 409
            return response
    else:
        payload = {'error': 'Json file does not contain all necessary information'}
        response = HttpResponse(json.dumps(payload),content_type='application/json')
        response.status_code = 400
        return response

   s = Schnorr()
   parameters = {'p': int(election.p),'q':int(election.q),'g':int(election.g)}
   keys = s.generate_keys(parameters)

   send_mail(
    'E-Voting on Fenix Credentials',
    "You're credentials for the election with id " + election.uuid + " are:\n"+
    "Secret:" + keys["priv"]["a"] + "\n" +
    "Public:" + keys["pub"]["beta"],
    'no-reply@tecnico.ulisboa.pt',
    [voter.email],
    fail_silently=False,)
   payload = {
       'voterId': voter.voterId,
       'electionId': electionId,
       'public credential': keys["pub"]["beta"]
    }
   return HttpResponse(json.dumps(payload),content_type='application/json')

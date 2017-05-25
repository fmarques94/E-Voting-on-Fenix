from django.http import HttpResponse
from Registration import parser

def addElection(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        if data:
            return parseElectionJson(json.loads(data))
        else:
            payload = {'error:' : 'No data received'}
            response = HttpResponse(json.dumps(payload),content_type='application/json')
            response.status_code = 400
            return response
    else:
        payload = {'error:' : request.method + ' request method not supported'}
        response = HttpResponse(json.dumps(payload),content_type='application/json')
        response.status_code = 405
        return response
    
def createCredentials(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        if data:
            parseCredentialRequest(json.loads(data))
        else:
            payload = {'error:' : 'No data received'}
            response = HttpResponse(json.dumps(payload),content_type='application/json')
            response.status_code = 400
            return response
    else:
        payload = {'error:' : request.method + ' request method not supported'}
        response = HttpResponse(json.dumps(payload),content_type='application/json')
        response.status_code = 405
        return response
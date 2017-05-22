from ElectionServer.models import Election,Question,Answer,EligibleVoter,Trustee
from ElectionServer.exceptions import TrusteeAlreadyPresentError
from django.db.utils import IntegrityError
import csv

def parseQuestion(jsonData,election_id):
    question = Question()
    question.election = Election.objects.get(uuid=election_id)
    question.question = jsonData['question']
    question.save()
    for key in jsonData['answer']:
        answer = Answer()
        answer.question = question
        answer.answer = jsonData['answer'][key]
        answer.save()

def parseVoterFile(csvfile,election_id):
    election = Election.objects.get(uuid=election_id)
    reader = csv.reader(csvfile.read().decode('utf-8-sig').split('\n'),delimiter=";")
    for row in reader:
        if(len(row)>0):
            voter = EligibleVoter()
            voter.election = election
            voter.voterId = row[0]
            voter.name = row[1]
            voter.email = row[2]
            voter.voted = False
            voter.save()

def parseTrustees(jsonData,election):
    if "addTrustees" in jsonData:
        print("Going to add Trustee")
        addTrustee(jsonData,election)
    elif "removeTrustee" in jsonData:
        removeTrustee(jsonData,election)
    else:
        raise InvalidJson

def removeTrustee(jsonData,thisElection):
    Trustee.objects.get(trusteeId=jsonData["removeTrustee"], election=thisElection).delete()

def addTrustee(jsonData,election):
    print(jsonData)
    for value in jsonData["addTrustees"]:
        try:
            trustee = Trustee()
            trustee.election = election
            trustee.trusteeId = value['trusteeId']
            trustee.name = value['name']
            trustee.email = value['email']
            trustee.save()
            return True;
        except IntegrityError:
            raise TrusteeAlreadyPresentError()
    

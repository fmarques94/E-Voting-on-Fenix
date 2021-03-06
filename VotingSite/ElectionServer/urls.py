from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

uuidRegEx = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
idRegEx = 'ist1\d+'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^elections/$', views.elections, name='elections'),
    url(r'^create/$', views.createElection, name='createElection'),
    url(r'^getElections/$', views.getElections, name='getElections'),
    url(r'^manageElections/$', views.manageElections, name='manageElections'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/$', views.election, name='election'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/manageTrustees/$', views.manageTrustees, name='manageTrustees'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/addTrustees/$', views.addTrustees, name='addTrustees'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/removeTrustees/$', views.removeTrustees, name='removeTrustees'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/getTrustees/$', views.getTrustees, name='getTrustees'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/trustee/$', views.trustee, name='trustee'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/manageVoters/$', views.manageVoters, name='manageVoters'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/addVoters/$', views.addVoters, name='addVoters'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/removeVoters/$', views.removeVoters, name='removeVoters'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/getVoters/$', views.getVoters, name='getVoters'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/manageQuestions/$', views.manageQuestions, name='manageQuestions'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/addQuestions/$', views.addQuestions, name='addQuestions'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/removeQuestions/$', views.removeQuestions, name='removeQuestions'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/getQuestions/$', views.getQuestions, name='getQuestions'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/register/$', views.register, name='register'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/ballotBox/$', views.cast, name='cast'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/setPublicKey/$', views.addElectionPublicKey, name='setPublicKey'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/bulletinBoard/$', views.bulletinBoard, name='bulletinBoard'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/auditBallot/$', views.auditBallot, name='auditBallot'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/manageTally/$', views.manageTally, name='manageTally'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/addPaperVoters/$', views.addPaperVoters, name='addPaperVoters'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/removePaperVoters/$', views.removePaperVoters, name='removePaperVoters'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/submitPaperResults/$', views.submitPaperResults, name='submitPaperResults'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/submitEncryptedTally/$', views.aggregateEncTally, name='submitEncryptedTally'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/submitPartialDecryption/$', views.submitPartialDecryption, name='submitPartialDecryption'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/publishResults/$', views.publishResults, name='publishResults'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/delete/$', views.deleteElection, name='deleteElection'),
    url(r'^trusteeElectionList/$', views.trusteeElectionList, name='trusteeList'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/trustee/$', views.trustee, name='trustee'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/exportData/$', views.exportData, name='exportData'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout',kwargs={'next_page': '/'}),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
]

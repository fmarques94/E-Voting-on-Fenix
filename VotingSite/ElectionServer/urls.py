from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

uuidRegEx = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
idRegEx = 'ist1\d+'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^create/$', views.create, name='create'),
    url(r'^getElections/$', views.getElections, name='getElections'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/$', views.election, name=election),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/addTrustees/$', views.addTrustees, name=addTrustees),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/removeTrustees/$', views.removeTrustees, name=removeTrustees),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/trustee/$', views.trustee, name=trustee),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/addVoters/$', views.addVoters, name=addVoters),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/removeVoters/$', views.removeVoters, name=removeVoters),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/addQuestion/$', views.addQuestion, name=addQuestion),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/removeQuestion/$', views.removeQuestion, name=removeQuestion),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/register/$', views.register, name=register),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/cast/$', views.cast, name=cast),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout',kwargs={'next_page': '/'}),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    #url(r'^manage/$',views.manage_list, name='manage'),
    #url(r'^manage/(?P<election_id>'+uuidRegEx+')/$',views.manage, name='manage'),
    #url(r'^election/(?P<election_id>'+uuidRegEx+')/$',views.election, name='election'),
    #url(r'^manage/(?P<election_id>'+uuidRegEx+')/questions/$',views.manageQuestions, name='manageQuestions'),
    #url(r'^manage/(?P<election_id>'+uuidRegEx+')/voters/$',views.addVoters, name='addVoters'),
    #url(r'^manage/(?P<election_id>'+uuidRegEx+')/trustees/$',views.manageTrustees, name='manageTrustees'),
    #url(r'^manage/(?P<election_id>'+uuidRegEx+')/trustees/(?P<trustee_id>'+idRegEx+')/$',views.trustee, name='trustee'),
    #url(r'^manage/(?P<election_id>'+uuidRegEx+')/cast/$',views.cast, name='cast')
    #url(r'^manage/(?P<election_id>'+uuidRegEx+')/register/$',views.register, name='register')
    #url(r'^login/$', views.login, name='login'),
    #url(r'^logout/$', auth_views.logout, name='logout',kwargs={'next_page': '/'}),
    #url(r'^oauth/', include('social_django.urls', namespace='social')),
]

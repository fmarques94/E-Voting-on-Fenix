from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

uuidRegEx = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
idRegEx = 'ist1\d+'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^create/$',views.createElection, name='create'),
    url(r'^manage/$',views.manage_list, name='manage'),
    url(r'^manage/(?P<election_id>'+uuidRegEx+')/$',views.manage, name='manage'),
    url(r'^election/(?P<election_id>'+uuidRegEx+')/$',views.election, name='election'),
    url(r'^manage/(?P<election_id>'+uuidRegEx+')/questions/$',views.manageQuestions, name='manageQuestions'),
    url(r'^manage/(?P<election_id>'+uuidRegEx+')/voters/$',views.addVoters, name='addVoters'),
    url(r'^manage/(?P<election_id>'+uuidRegEx+')/trustees/$',views.manageTrustees, name='manageTrustees'),
    url(r'^manage/(?P<election_id>'+uuidRegEx+')/trustees/(?P<trustee_id>'+idRegEx+')/$',views.trustee, name='trustee'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout',kwargs={'next_page': '/'}),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
]

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout',kwargs={'next_page': '/'}),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
]

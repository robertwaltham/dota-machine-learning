__author__ = 'leveltenpaladin'
from django.conf.urls import patterns, url

from DotaStats import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view() , name='index'),
    url(r'^get_match/$', views.get_match, name='get_match'),

)
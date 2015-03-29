__author__ = 'leveltenpaladin'
from django.conf.urls import patterns, url

from DotaStats import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view() , name='index'),
    url(r'^load-matches/$', views.LoadMatchesFromAPI.as_view(), name='load-matches'),
    url(r'^process-match/$', views.LoadDetailsForMatch.as_view(), name='process-match'),
    url(r'^matches', views.AjaxGetMatchList.as_view(), name='matches')

)
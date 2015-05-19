__author__ = 'Robert Waltham'
from django.conf.urls import patterns, url

from DotaStats import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view() , name='index'),
    url(r'^load-matches/$', views.AjaxLoadMatchesFromAPI.as_view(), name='load-matches'),
    url(r'^process-match/$', views.AjaxLoadDetailsForAll.as_view(), name='process-match'),
    url(r'^match-list', views.AjaxGetMatchList.as_view(), name='match-list-json'),
    url(r'^match-count', views.AjaxGetMatchCount.as_view(), name='match_count'),
    url(r'^load-static-data/$', views.AjaxLoadStaticDataView.as_view(), name='static-data'),
    url(r'^update-match/(?P<pk>\d+)/', views.AjaxUpdateMatchDetails.as_view(), name='update-match'),
    url(r'^hero/(?P<pk>\d+)/', views.HeroDetailView.as_view(), name='hero-detail'),
    url(r'^match/(?P<pk>\d+)/', views.MatchDetailView.as_view(), name='match-detail'),
    url(r'^build/', views.BuildDataView.as_view(), name='build-data'),
    url(r'^test/', views.BuildAndTestView.as_view(), name='build-test'),
    url(r'^items/', views.ItemListView.as_view(), name='items'),
    url(r'^heroes/', views.HeroListView.as_view(), name='heroes'),
    url(r'^matches/', views.MatchListView.as_view(), name='matches'),
    url(r'^predict/', views.CreatePredictionView.as_view(), name='create_prediction'),
    url(r'^login/', views.LogInView.as_view(), name='login'),
    url(r'^logout/', views.LogOutView.as_view(), name='logout'),
)
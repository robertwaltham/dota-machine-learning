__author__ = 'Robert Waltham'
from django.conf.urls import patterns, url, include
from rest_framework import routers
from DotaStats import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'matches', views.MatchViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'heroes', views.HeroViewSet)
router.register(r'items', views.ItemViewSet)

urlpatterns = patterns('',
                       url(r'^$', views.IndexView.as_view(), name='index'),
                       url(r'^load-matches/$', views.AjaxLoadMatchesFromAPI.as_view(), name='load-matches'),
                       url(r'^process-match/$', views.AjaxLoadDetailsForAll.as_view(), name='process-match'),
                       url(r'^load-static-data/$', views.AjaxLoadStaticDataView.as_view(), name='static-data'),
                       url(r'^update-match/(?P<pk>\d+)/', views.AjaxUpdateMatchDetails.as_view(), name='update-match'),
                       url(r'^login/', views.LogInView.as_view(), name='login'),
                       url(r'^logout/', views.LogOutView.as_view(), name='logout'),
                       url(r'^api/', include(router.urls), name='api'),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
                       )

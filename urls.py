__author__ = 'Robert Waltham'
from django.conf.urls import patterns, url, include
from rest_framework import routers
from DotaStats import views

router = routers.DefaultRouter()
router.register(r'matches', views.MatchViewSet)
router.register(r'heroes', views.HeroViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'herorecentmatches', views.HeroRecentMatchesSet, base_name='herorecentmatches')
router.register(r'itemrecentmatches', views.ItemRecentMatchSet, base_name='itemrecentmatches')
router.register(r'matchcreatedbydate', views.MatchDateCountSet, base_name='matchcreatedbydate')
router.register(r'taskmeta', views.TaskMetaSet, base_name='taskmeta')


urlpatterns = patterns('',
                       url(r'^$', views.IndexView.as_view(), name='index'),
                       url(r'^admin/$', views.AdminView.as_view(), name='admin'),
                       url(r'^load-matches/$', views.AjaxLoadMatchesFromAPI.as_view(), name='load-matches'),
                       url(r'^load-static-data/$', views.AjaxLoadStaticDataView.as_view(), name='static-data'),
                       url(r'^build/', views.BuildDataView.as_view(), name='build-data'),
                       url(r'^login/', views.LogInView.as_view(), name='login'),
                       url(r'^logout/', views.LogOutView.as_view(), name='logout'),
                       url(r'^api/', include(router.urls), name='api'),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
                       )

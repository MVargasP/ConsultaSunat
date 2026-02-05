from django.urls import path,include
from apps.common.views import HomeView
 
extra_patterns = [
    path('',include('apps.sunat.urls')),
    path('company/',include('apps.company.urls')),
    path('user/',include('apps.user.urls')),

    ]
urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('api/', include(extra_patterns)),

] 
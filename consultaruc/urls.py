from django.urls import path,include
 
extra_patterns = [
    path('',include('apps.sunat.urls')),
    path('company/',include('apps.company.urls')),
    path('user/',include('apps.user.urls')),

    ]
urlpatterns = [
    path('api/', include(extra_patterns)),

] 
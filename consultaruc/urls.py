from django.urls import path,include
 
extra_patterns = [
    path('',include('apps.sunat.urls')),
    path('company/',include('apps.company.urls')),

    ]
urlpatterns = [
    path('api/', include(extra_patterns)),

] 
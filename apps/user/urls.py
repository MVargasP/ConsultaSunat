from django.urls import path
from knox import views as knox_views
from .views.login import LoginAPIView
from .views.user import RegisterClaveAPIView
urlpatterns = [
    #path('', include('knox.urls')),
    #path('user', UserAPIView.as_view()),
    path('register/', RegisterClaveAPIView.as_view()),
    path('login/', LoginAPIView.as_view(), name='knox_login'),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logout_all/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
]
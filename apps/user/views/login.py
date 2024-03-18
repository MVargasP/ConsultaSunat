from rest_framework import generics, permissions,status
from knox.views import LoginView as KnoxLoginView
from ..serializers.login import LoginSerializer
from ..serializers.user import ListUserSerializer
from django.contrib.auth import login
from rest_framework.response import Response

class LoginAPIView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):               
            user = serializer.validated_data

            login(request, user)
            supers=super(LoginAPIView, self).post(request, format=None)
            data=supers.data
            
            return Response({
                "usuario":ListUserSerializer(user).data,
                "token": data,
            })
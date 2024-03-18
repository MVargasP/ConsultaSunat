from rest_framework import generics, permissions,status 
from rest_framework.response import Response  
#from rest_framework_api_key.models import APIKey
#from rest_framework_api_key.permissions import HasAPIKey

from knox.models import AuthToken
from ..serializers.user import RegisterClaveSerializer

#API para crear usuario, evia un correo asincrono con celery y redis , brindando las credenciales
class RegisterClaveAPIView(generics.CreateAPIView):
    serializer_class = RegisterClaveSerializer
    permission_classes = [  permissions.IsAuthenticated ]
    #permission_classes = [HasAPIKey]
    #api_key, key = APIKey.objects.create_key(name="my-remote-service")

    #print(key)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)       
        serializer.is_valid(raise_exception=True)       
        user = serializer.save()

        return Response({
            "user": RegisterClaveSerializer(user, context=self.get_serializer_context()).data, 
            #"token": AuthToken.objects.create(user)[1],
            "message": "Registro exitoso"
        })
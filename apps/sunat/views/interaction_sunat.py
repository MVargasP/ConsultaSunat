#Django
from django.db.models import F
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from ..serializers.interaction_sunat import ConsultaSunatSerializer
from ..models import InteractionSunat,Ruc

#models
from apps.company.models import Company

#helpers
from helper.external_request import consultar_datos_ruc


#from rest_framework_api_key.permissions import HasAPIKey
#from rest_framework.permissions import IsAuthenticated

class ConsultaRucView(APIView):
    #permission_classes = [HasAPIKey | IsAuthenticated]
    
    def post(self, request, format=None):
        # Extrae la clave API del encabezado Authorization
        #key = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[-1]
        #api_key = EmpresaAPIKey.objects.get_from_key(key)
        
        # Aquí puedes usar api_key para realizar operaciones específicas,
        # como verificar a qué empresa o proyecto está asociada
        
        serializer = ConsultaSunatSerializer(data=request.data)
        if serializer.is_valid():
            if not serializer.validated_data.get('token')=='hqHfONaufIuSyoZ3YeFmOAwGaPqweLgQmWtNMfaytziBaSHwQ1hmFo3GpfwU':
                return Response({"token":"token no valido"}, status=status.HTTP_400_BAD_REQUEST)
            numero_documento = serializer.validated_data.get('numero_documento')
            datos = consultar_datos_ruc(numero_documento)
            if datos:
                InteractionSunat.objects.create(document_number=numero_documento,company_id=1,payload=datos)
                Ruc.objects.get_or_create(document_number=numero_documento,defaults={'payload':datos})

                Company.objects.filter(id=1).update(total_sunat=F('total_sunat') + 1)

                return Response(datos, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Django
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from ..serializers.interaction_sunat import ConsultaSunatSerializer

#models
from ..models import Ruc

#helpers
from helper.external_request import consultar_datos_ruc

from ..util import ConsultaRUC,update_models
#from rest_framework_api_key.permissions import HasAPIKey
#from rest_framework.permissions import IsAuthenticated
from threading import Thread

class ConsultaRucView(APIView):
    #permission_classes = [HasAPIKey | IsAuthenticated]
    
    def post(self, request, format=None):
        # Extrae la clave API del encabezado Authorization
        #key = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[-1]
        #api_key = EmpresaAPIKey.objects.get_from_key(key)
        
        # Aquí puedes usar api_key para realizar operaciones específicas,
        # como verificar a qué empresa o proyecto está asociada
        # Ejemplo de uso
        consulta_ruc = ConsultaRUC()
        serializer = ConsultaSunatSerializer(data=request.data)
        if serializer.is_valid():
            if not serializer.validated_data.get('token')=='hqHfONaufIuSyoZ3YeFmOAwGaPqweLgQmWtNMfaytziBaSHwQ1hmFo3GpfwU':
                return Response({"token":"token no valido"}, status=status.HTTP_400_BAD_REQUEST)
            numero_documento = serializer.validated_data.get('numero_documento')
            ruc_model = Ruc.objects.filter(document_number=numero_documento)
            if ruc_model:
                ruc_model = ruc_model.first()
                response = ruc_model.payload
                made_scraping =False
            else:
                response = consulta_ruc.obtener_datos_por_ruc(numero_documento)
                made_scraping =True
                Ruc.objects.create(document_number=numero_documento,payload= response)

                #datos = consultar_datos_ruc(numero_documento)
            thread = Thread(target=update_models, args=(numero_documento,response,made_scraping))
            thread.start()
            return Response(response, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
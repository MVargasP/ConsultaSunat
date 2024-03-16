from rest_framework import serializers

class ConsultaSunatSerializer(serializers.Serializer):
    numero_documento = serializers.CharField()
    token = serializers.CharField()